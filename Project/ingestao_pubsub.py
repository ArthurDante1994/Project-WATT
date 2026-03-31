import os
import json
import logging
from google.cloud import pubsub_v1
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Configuração de Logs detalhados para diagnóstico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Configurações do Pub/Sub
PROJECT_ID = "deeenergyanalysis"
# ATENÇÃO: Você ainda precisa descobrir esse nome com a WATT!
SUBSCRIPTION_ID = "Danilo"

# Aliases válidos para identificação do dispositivo conforme documentação
DEVICE_ID_ALIASES = ["Nome", "deviceId", "device_id", "idDispositivo", "dispositivold", "gatewayId"]

def extract_device_id(payload):
    """Verifica e extrai o identificador do dispositivo usando os aliases permitidos."""
    for alias in DEVICE_ID_ALIASES:
        if alias in payload and payload[alias]:
            return payload[alias]
    return None

def normalize_scale_factors(payload):
    """Garante que RTC e RTP sejam válidos (padrão 1.0 se ausentes ou <= 0)."""
    for factor in ['RTC', 'RTP']:
        try:
            val = float(payload.get(factor, 1.0))
            payload[factor] = val if val > 0 else 1.0
        except (ValueError, TypeError):
            payload[factor] = 1.0
    return payload

def process_message(message: pubsub_v1.subscriber.message.Message):
    """Callback executado a cada nova mensagem recebida."""
    try:
        # Tenta decodificar o payload JSON
        payload_str = message.data.decode('utf-8')
        payload = json.loads(payload_str)
        
        # Validação 1: Estrutura mínima (Identificador do dispositivo)
        device_id = extract_device_id(payload)
        if not device_id:
            logger.warning(f"Mensagem descartada: Identificador do dispositivo ausente. Payload: {payload_str}")
            message.ack() # Confirma recebimento para não reprocessar lixo
            return

        # Normalização dos fatores de escala (RTC/RTP)
        payload = normalize_scale_factors(payload)
        
        # Log de sucesso no processamento
        logger.info(f"Leitura processada com sucesso | Dispositivo: {device_id} | RTC: {payload['RTC']} | RTP: {payload['RTP']}")
        
        # TODO: Encaminhar o 'payload' normalizado para o Bloco 2 (Persistência em Banco de Dados)
        
        # ESTA LINHA PARA VER O PAYLOAD COMPLETO:
        print(json.dumps(payload, indent=4))
        

        # Confirma que a mensagem foi processada corretamente
        message.ack()

    except json.JSONDecodeError:
        logger.error(f"Falha de validação: Payload não é um JSON válido. Dados brutos: {message.data}")
        message.ack() # Descarta a mensagem inválida
    except Exception as e:
        logger.error(f"Erro inesperado ao processar mensagem: {e}", exc_info=True)
        # Em caso de erro sistêmico temporário, fazemos nack() para que a mensagem seja reenviada
        message.nack()

def start_subscriber():
    """Inicializa o subscriber de forma contínua."""
    # Verifica se as credenciais foram configuradas no ambiente
    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        logger.error("A variável de ambiente GOOGLE_APPLICATION_CREDENTIALS não está definida. O serviço será encerrado.")
        return

    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)

    logger.info(f"Iniciando serviço de ingestão no tópico: {subscription_path}")
    
    # Inicia a escuta contínua de mensagens
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=process_message)

    try:
        # Mantém o processo rodando
        streaming_pull_future.result()
    except KeyboardInterrupt:
        logger.info("Serviço de ingestão interrompido pelo usuário.")
        streaming_pull_future.cancel()
    except Exception as e:
        logger.critical(f"Falha crítica no subscriber: {e}")
        streaming_pull_future.cancel()

if __name__ == "__main__":
    start_subscriber()