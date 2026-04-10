import copy
import json
import logging
import os
import random
import time
from datetime import datetime

import servidor_modbus
from dotenv import load_dotenv

# Carrega variaveis do .env (se houver)
load_dotenv(override=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

DEVICE_ID_ALIASES = [
    "Nome",
    "deviceId",
    "device_id",
    "idDispositivo",
    "dispositivoId",
    "dispositivold",
    "gatewayId",
]

BASE_PAYLOAD = {
    "Nome": "Medidor Galpao",
    "IP": "10.27.41.45",
    "Canal": "11",
    "MAC": "E8:9F:6D:6B:E5:48",
    "SSID": "controle",
    "GTW": "5E:CF:7F:14:F8:86",
    "Rede": "W",
    "RTC": 60.0,
    "RTP": 1.0,
    "Va": "223.01",
    "Vb": "221.59",
    "Vc": "223.25",
    "Ia": "0.24",
    "Ib": "0.34",
    "Ic": "0.34",
    "In": "0.09",
    "angVa": "0.0",
    "angVb": "119.9",
    "angVc": "239.6",
    "angIa": "3.0",
    "angIb": "350.9",
    "angIc": "8.9",
    "Pdir": "204.63",
    "Prev": "0",
    "Q": "3.77",
    "S": "207.50",
    "Ph": "0.03",
    "fpa": "0.997",
    "fpb": "0.978",
    "fpc": "0.984",
    "fpt": "0.985",
    "f": "59.99",
    "t": "32.00",
    "Pa": "54.505",
    "Pb": "74.588",
    "Pc": "75.555",
    "Ea": "62.277",
    "Eb": "89.765",
    "Ec": "67.648",
    "Ear": "0.000",
    "Ebr": "0.000",
    "Ecr": "0.000",
    "Era": "1.009",
    "Erb": "0.384",
    "Erc": "6.324",
    "Erar": "2.851",
    "Erbr": "4.992",
    "Ercr": "0.144",
}

RANGED_FIELDS = {
    "Va": (218.0, 231.0, 2),
    "Vb": (218.0, 231.0, 2),
    "Vc": (218.0, 231.0, 2),
    "Ia": (0.05, 2.50, 2),
    "Ib": (0.05, 2.50, 2),
    "Ic": (0.05, 2.50, 2),
    "In": (0.00, 0.80, 2),
    "Pdir": (20.0, 900.0, 2),
    "Q": (0.0, 150.0, 2),
    "S": (20.0, 1100.0, 2),
    "f": (59.80, 60.20, 2),
    "t": (28.0, 40.0, 2),
    "Pa": (10.0, 350.0, 3),
    "Pb": (10.0, 350.0, 3),
    "Pc": (10.0, 350.0, 3),
    "Ea": (1.0, 250.0, 3),
    "Eb": (1.0, 250.0, 3),
    "Ec": (1.0, 250.0, 3),
    "fpa": (0.85, 1.0, 3),
    "fpb": (0.85, 1.0, 3),
    "fpc": (0.85, 1.0, 3),
    "fpt": (0.85, 1.0, 3),
}


class SimulatedMessage:
    """Objeto minimo para simular a API do Pub/Sub usada no callback."""

    def __init__(self, payload_dict):
        self.data = json.dumps(payload_dict, ensure_ascii=False).encode("utf-8")
        self.acked = False
        self.nacked = False

    def ack(self):
        self.acked = True

    def nack(self):
        self.nacked = True


def extract_device_id(payload):
    for alias in DEVICE_ID_ALIASES:
        if alias in payload and payload[alias]:
            return payload[alias]
    return None


def normalize_scale_factors(payload):
    for factor in ["RTC", "RTP"]:
        try:
            val = float(payload.get(factor, 1.0))
            payload[factor] = val if val > 0 else 1.0
        except (ValueError, TypeError):
            payload[factor] = 1.0
    return payload


def _random_str(min_val, max_val, decimals):
    return f"{random.uniform(min_val, max_val):.{decimals}f}"


def build_simulated_payload(counter):
    payload = copy.deepcopy(BASE_PAYLOAD)

    for field, (min_val, max_val, decimals) in RANGED_FIELDS.items():
        payload[field] = _random_str(min_val, max_val, decimals)

    payload["timestamp"] = datetime.now().isoformat()
    payload["simulacao"] = True
    payload["sequencia"] = counter

    return payload


def process_message(message):
    """Fluxo equivalente ao callback real, mas recebendo mensagem simulada."""
    try:
        payload_str = message.data.decode("utf-8")
        payload = json.loads(payload_str)

        device_id = extract_device_id(payload)
        if not device_id:
            logger.warning(
                "[SIMULACAO] Mensagem descartada: identificador do dispositivo ausente. Payload: %s",
                payload_str,
            )
            message.ack()
            return

        payload = normalize_scale_factors(payload)

        logger.info(
            "Leitura processada com sucesso | Dispositivo: %s | RTC: %s | RTP: %s",
            device_id,
            payload["RTC"],
            payload["RTP"],
        )
        logger.info("Leitura recebida | Dispositivo: %s", device_id)

        logger.info("[SIMULACAO] Persistencia em banco desativada para mensagens simuladas")

        servidor_modbus.atualizar_registradores(payload)
        print(json.dumps(payload, indent=4, ensure_ascii=False))

        message.ack()

    except json.JSONDecodeError:
        logger.error("[SIMULACAO] Falha de validação: payload não é JSON válido. Dados brutos: %s", message.data)
        message.ack()
    except Exception as exc:
        logger.error("[SIMULACAO] Erro inesperado ao processar mensagem: %s", exc, exc_info=True)
        message.nack()


def start_simulation():
    interval_seconds = float(os.getenv("SIM_INTERVAL_SECONDS", "2"))
    max_messages = int(os.getenv("SIM_MAX_MESSAGES", "0"))

    logger.info("MODO SIMULACAO ATIVO | Intervalo: %ss | Limite de mensagens: %s", interval_seconds, max_messages or "infinito")

    servidor_modbus.iniciar_servidor()

    counter = 0
    try:
        while True:
            counter += 1
            payload = build_simulated_payload(counter)
            logger.info("[SIMULACAO] Enviando mensagem simulada #%s", counter)

            sim_message = SimulatedMessage(payload)
            process_message(sim_message)

            if max_messages > 0 and counter >= max_messages:
                logger.info("[SIMULACAO] Limite configurado de mensagens atingido. Encerrando.")
                break

            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        logger.info("[SIMULACAO] Execucao interrompida pelo usuario.")


if __name__ == "__main__":
    start_simulation()
