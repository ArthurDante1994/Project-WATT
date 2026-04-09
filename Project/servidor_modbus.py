from pyModbusTCP.server import ModbusServer
from pyModbusTCP.utils import encode_ieee, long_list_to_word
import logging

logger = logging.getLogger(__name__)

MAPA_MODBUS = {
    'RTC': 0, 'RTP': 2,
    'Va': 10, 'Vb': 12, 'Vc': 14,
    'Ia': 20, 'Ib': 22, 'Ic': 24, 'In': 26,
    'Pa': 30, 'Pb': 32, 'Pc': 34, 'Pdir': 36,
    'fpa': 40, 'fpb': 42, 'fpc': 44, 'fpt': 46,
    'f': 50, 't': 52,
    'Ea': 60, 'Eb': 62, 'Ec': 64
}

server = None

def iniciar_servidor(host="127.0.0.1", port=10502):
    global server
    server = ModbusServer(host=host, port=port, no_block=True)
    server.start()
    logger.info(f"🟢 Servidor Modbus TCP iniciado em {host}:{port}")

def aplicar_fatores_escala(payload):
    rtc = float(payload.get('RTC', 60.0))
    rtp = float(payload.get('RTP', 1.0))
    
    payload_escalado = {}
    for key, value in payload.items():
        try:
            val = float(value)
            if key in ['Va', 'Vb', 'Vc']:
                payload_escalado[key] = val * rtp
            elif key in ['Ia', 'Ib', 'Ic', 'In']:
                payload_escalado[key] = val * rtc
            elif key.startswith('P') or key.startswith('E') or key in ['Q', 'S', 'Ph']:
                payload_escalado[key] = val * (rtc * rtp)
            else:
                payload_escalado[key] = val
        except (ValueError, TypeError):
            continue
            
    return payload_escalado

def atualizar_registradores(payload):
    if not server: 
        return
        
    payload_escalado = aplicar_fatores_escala(payload)
    
    for variavel, endereco in MAPA_MODBUS.items():
        if variavel in payload_escalado:
            # 1. Multiplica por 100 e transforma em Inteiro (ex: 226.35 vira 22635)
            valor_int = int(float(payload_escalado[variavel]) * 100)
            
            # 2. Divide esse Inteiro de 32-bits nas duas gavetas do Modbus
            words = [(valor_int >> 16) & 0xFFFF, valor_int & 0xFFFF]
            
            # 3. Grava na memória
            server.data_bank.set_holding_registers(endereco, words)