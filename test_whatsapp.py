import logging
import sys
import os
from datetime import datetime
from src.config import Config
from src.notifier.whatsapp import WhatsAppNotifier

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)

def test_whatsapp_connection():
    """
    Tenta enviar uma mensagem de teste para o WhatsApp.
    """
    logger.info("Iniciando teste de conexão com Evolution API...")
    
    try:
        config = Config()
        
        notifier = WhatsAppNotifier(config)
        
        # Mensagem de teste
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        test_msg = (
            f"*Teste de Integração Evolution API*\n\n"
            f"Conexão estabelecida com sucesso!\n"
            f" Horário do teste: {timestamp}\n\n"
            f"Se você recebeu esta mensagem, o bot está pronto para enviar notificações de reserva. "
        )
        
        success = notifier.send_message(test_msg)
        
        if success:
            logger.info("TESTE CONCLUÍDO COM SUCESSO!")
            return True
        else:
            logger.error("O teste falhou. Verifique os logs e sua API Key.")
            return False
            
    except ValueError as e:
        logger.error(f"Erro de configuração: {e}")
        logger.info("Dica: Certifique-se de que todas as variáveis EVOLUTION_* e WHATSAPP_* estão no seu .env ou GitHub Secrets.")
        return False
    except Exception as e:
        logger.exception(f"Ocorreu um erro inesperado: {e}")
        return False

if __name__ == "__main__":
    success = test_whatsapp_connection()
    if not success:
        sys.exit(1)
