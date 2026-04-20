import requests
import logging
from src.config import Config

logger = logging.getLogger(__name__)

class WhatsAppNotifier:
    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.evolution_url.rstrip('/')
        self.instance = config.evolution_instance
        self.api_key = config.evolution_key
        self.group_jid = config.whatsapp_group_jid

    def send_message(self, text: str):
        """
        Envia uma mensagem de texto para o grupo configurado via Evolution API v2.
        """
        url = f"{self.base_url}/message/sendText/{self.instance}"
        
        headers = {
            "Content-Type": "application/json",
            "apikey": self.api_key
        }
        
        payload = {
            "number": self.group_jid,
            "text": text,
            "delay": 1200,
            "linkPreview": False
        }

        try:
            logger.info(f"Enviando mensagem para o grupo WhatsApp: {self.group_jid}")
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code in [200, 201]:
                logger.info("Mensagem enviada com sucesso para o WhatsApp.")
                return True
            else:
                logger.error(f"Erro ao enviar mensagem para o WhatsApp. Status: {response.status_code}, Resposta: {response.text}")
                return False
                
        except Exception:
            logger.exception("Falha na comunicação com a Evolution API")
            return False
