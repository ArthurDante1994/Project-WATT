import json
import logging
import sqlite3
import random
import copy
from datetime import datetime

# Importa o seu servidor modbus para atualizar o dado em tempo real no Elipse
try:
    import servidor_modbus
except ImportError:
    servidor_modbus = None

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# CONFIGURAÇÃO DO SEU BANCO ATUAL
DB_PATH = "watt_energia.db" 
DEVICE_NAME = "Medidor Galpao"

def gerar_payload_realista():
    """Gera o JSON simulado com Corrente de 0-80A e Tensões de 220V"""
    # Payload base seguindo o seu padrão
    payload = {
        "Nome": DEVICE_NAME,
        "IP": "10.27.41.45",
        "RTC": 60.0,
        "RTP": 1.0,
        "timestamp": datetime.now().isoformat()
    }
    
    # Valores aleatórios dentro dos ranges solicitados
    va = round(random.uniform(218.0, 226.0), 2)
    vb = round(random.uniform(218.0, 226.0), 2)
    vc = round(random.uniform(218.0, 226.0), 2)
    
    ia = round(random.uniform(0.0, 80.0), 2)
    ib = round(random.uniform(0.0, 80.0), 2)
    ic = round(random.uniform(0.0, 80.0), 2)
    
    fpt = round(random.uniform(0.80, 0.99), 3)
    p_total = round((va*ia + vb*ib + vc*ic) * fpt, 2)
    
    # Atualiza o payload com os dados elétricos
    payload.update({
        "Va": str(va), "Vb": str(vb), "Vc": str(vc),
        "Ia": str(ia), "Ib": str(ib), "Ic": str(ic),
        "fpt": str(fpt),
        "Pdir": str(p_total),
        "Ea": str(round(random.uniform(64.0, 65.0), 3))
    })
    return payload

def salvar_no_seu_db(payload):
    """Salva no banco watt_energia.db respeitando o schema de ativos e histórico"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. Garante que o ativo existe e pega o ID dele
        cursor.execute('INSERT OR IGNORE INTO ativos (device_id) VALUES (?)', (DEVICE_NAME,))
        cursor.execute('SELECT id FROM ativos WHERE device_id = ?', (DEVICE_NAME,))
        ativo_id = cursor.fetchone()[0]
        
        # 2. Insere na tabela leituras_historicas
        query_hist = """
            INSERT INTO leituras_historicas (ativo_id, timestamp, rtc, rtp, payload_completo)
            VALUES (?, ?, ?, ?, ?)
        """
        cursor.execute(query_hist, (
            ativo_id, 
            payload["timestamp"], 
            payload["RTC"], 
            payload["RTP"], 
            json.dumps(payload)
        ))
        
        # 3. Atualiza o estado_atual (Upsert)
        query_atual = """
            INSERT INTO estado_atual (ativo_id, timestamp_ultima_leitura, payload_completo)
            VALUES (?, ?, ?)
            ON CONFLICT(ativo_id) DO UPDATE SET
                timestamp_ultima_leitura = excluded.timestamp_ultima_leitura,
                payload_completo = excluded.payload_completo
        """
        cursor.execute(query_atual, (ativo_id, payload["timestamp"], json.dumps(payload)))
        
        conn.commit()
        conn.close()
        logger.info(f"Sucesso! Salvo no banco {DB_PATH} (ID Ativo: {ativo_id})")
        
    except Exception as e:
        logger.error(f"Erro ao salvar no banco: {e}")

def publicar_uma_vez():
    logger.info("Iniciando publicação única...")
    
    # 1. Gera o dado
    payload = gerar_payload_realista()
    
    # 2. Salva no banco watt_energia.db
    salvar_no_seu_db(payload)
    
    # 3. Atualiza o Modbus (Se o servidor estiver rodando)
    if servidor_modbus:
        try:
            servidor_modbus.atualizar_registradores(payload)
            logger.info("Servidor Modbus local atualizado.")
        except:
            logger.warning("Não foi possível atualizar o Modbus (servidor offline).")

    print(f"\n--- DADO SIMULADO (Corrente: {payload['Ia']} A) ---")
    print(json.dumps(payload, indent=4))
    print("--------------------------------------------------\n")

if __name__ == "__main__":
    publicar_uma_vez()