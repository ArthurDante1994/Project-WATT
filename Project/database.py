import sqlite3
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

DB_PATH = "watt_energia.db"

def init_db():
    """Inicializa o banco de dados e cria o schema exigido."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tabela 1: Ativos (Dispositivos monitorados)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ativos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT UNIQUE NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabela 2: Leituras Históricas
    # A chave composta UNIQUE(ativo_id, timestamp) evita duplicidade de dados no mesmo instante
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leituras_historicas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ativo_id INTEGER NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            rtc REAL,
            rtp REAL,
            payload_completo TEXT NOT NULL,
            FOREIGN KEY (ativo_id) REFERENCES ativos (id),
            UNIQUE(ativo_id, timestamp)
        )
    ''')

    # Tabela 3: Estado Atual
    # Armazena apenas a última leitura de cada ativo (Inserção idempotente / Upsert)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estado_atual (
            ativo_id INTEGER PRIMARY KEY,
            timestamp_ultima_leitura TIMESTAMP NOT NULL,
            payload_completo TEXT NOT NULL,
            FOREIGN KEY (ativo_id) REFERENCES ativos (id)
        )
    ''')

    conn.commit()
    conn.close()
    logger.info("Banco de dados SQLite inicializado com sucesso.")

def get_or_create_ativo(device_id):
    """Busca o ID do ativo no banco, ou cria um novo se não existir."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tenta inserir. Se já existir (devido ao UNIQUE), ele ignora.
    cursor.execute('INSERT OR IGNORE INTO ativos (device_id) VALUES (?)', (device_id,))
    conn.commit()
    
    # Busca o ID do ativo
    cursor.execute('SELECT id FROM ativos WHERE device_id = ?', (device_id,))
    ativo_id = cursor.fetchone()[0]
    
    conn.close()
    return ativo_id

def salvar_leitura(device_id, payload):
    """
    Persiste os dados usando transações para garantir a integridade.
    Atualiza o histórico e o estado atual simultaneamente.
    """
    # Se o payload não trouxer timestamp, geramos um agora
    timestamp = payload.get('timestamp', datetime.now().isoformat())
    rtc = payload.get('RTC', 1.0)
    rtp = payload.get('RTP', 1.0)
    payload_json = json.dumps(payload)

    ativo_id = get_or_create_ativo(device_id)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Inicia uma transação explícita
        cursor.execute("BEGIN TRANSACTION;")

        # 1. Inserção no Histórico (Evita duplicidade com a restrição UNIQUE)
        cursor.execute('''
            INSERT OR IGNORE INTO leituras_historicas 
            (ativo_id, timestamp, rtc, rtp, payload_completo) 
            VALUES (?, ?, ?, ?, ?)
        ''', (ativo_id, timestamp, rtc, rtp, payload_json))

        # 2. Atualização Idempotente do Estado Atual (Upsert)
        cursor.execute('''
            INSERT INTO estado_atual (ativo_id, timestamp_ultima_leitura, payload_completo)
            VALUES (?, ?, ?)
            ON CONFLICT(ativo_id) DO UPDATE SET
                timestamp_ultima_leitura = excluded.timestamp_ultima_leitura,
                payload_completo = excluded.payload_completo
        ''', (ativo_id, timestamp, payload_json))

        # Confirma a transação
        conn.commit()
        
    except Exception as e:
        conn.rollback() # Se der erro em qualquer tabela, desfaz tudo
        logger.error(f"Erro ao salvar leitura no banco: {e}")
        raise
    finally:
        conn.close()

# Executa a criação das tabelas quando o arquivo é importado
init_db()