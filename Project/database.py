import sqlite3
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

DB_PATH = "watt_energia.db"

def init_db():
    """Inicializa o banco de dados com as Primary Keys e Constraints de Unicidade."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Tabela de Ativos (Dispositivos)
    # PRIMARY KEY: id (Autoincrement)
    # UNIQUE: device_id (Não permite dois medidores com o mesmo nome)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ativos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT UNIQUE NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. Tabela de Leituras Históricas
    # PRIMARY KEY: id
    # UNIQUE: (ativo_id, timestamp) -> Chave Composta que evita duplicidade no mesmo segundo
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

    # 3. Tabela de Estado Atual (Tempo Real)
    # PRIMARY KEY: ativo_id (Cada medidor tem apenas 1 linha com o dado mais recente)
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
    
    # Tenta inserir. Se já existir, ignora devido ao UNIQUE no device_id
    cursor.execute('INSERT OR IGNORE INTO ativos (device_id) VALUES (?)', (device_id,))
    conn.commit()
    
    # Busca o ID numérico (Primary Key) do ativo
    cursor.execute('SELECT id FROM ativos WHERE device_id = ?', (device_id,))
    ativo_id = cursor.fetchone()[0]
    
    conn.close()
    return ativo_id

def salvar_leitura(device_id, payload):
    """
    Persiste os dados usando transações. 
    USA 'INSERT OR IGNORE' para respeitar a UNIQUE CONSTRAINT de tempo.
    """
    timestamp = payload.get('timestamp', datetime.now().isoformat())
    rtc = payload.get('RTC', 1.0)
    rtp = payload.get('RTP', 1.0)
    payload_json = json.dumps(payload)

    # Obtém o ID da Primary Key da tabela ativos
    ativo_id = get_or_create_ativo(device_id)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("BEGIN TRANSACTION;")

        # 1. Inserção no Histórico
        # Se ativo_id + timestamp já existirem, o IGNORE impede a duplicata
        cursor.execute('''
            INSERT OR IGNORE INTO leituras_historicas 
            (ativo_id, timestamp, rtc, rtp, payload_completo) 
            VALUES (?, ?, ?, ?, ?)
        ''', (ativo_id, timestamp, rtc, rtp, payload_json))

        # 2. Atualização do Estado Atual (Upsert)
        # Aqui a Primary Key (ativo_id) garante que apenas o último dado exista
        cursor.execute('''
            INSERT INTO estado_atual (ativo_id, timestamp_ultima_leitura, payload_completo)
            VALUES (?, ?, ?)
            ON CONFLICT(ativo_id) DO UPDATE SET
                timestamp_ultima_leitura = excluded.timestamp_ultima_leitura,
                payload_completo = excluded.payload_completo
        ''', (ativo_id, timestamp, payload_json))

        conn.commit()
        
    except Exception as e:
        conn.rollback() 
        logger.error(f"Erro ao salvar leitura no banco: {e}")
        raise
    finally:
        conn.close()

# Inicializa o schema ao carregar o arquivo
init_db()