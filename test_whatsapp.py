# Teste de envio de notificacao por WhatsApp desativado.
# Todo o codigo foi mantido comentado para uma possivel reativacao futura.
#
# import logging
# import sys
# from datetime import datetime
# from src.config import Config
# from src.notifier.whatsapp import WhatsAppNotifier
#
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s | %(levelname)s | %(message)s",
# )
# logger = logging.getLogger(__name__)
#
# def test_whatsapp_connection():
#     """Tenta enviar uma mensagem de teste para o WhatsApp."""
#     logger.info("Iniciando teste de conexao com Evolution API...")
#     try:
#         config = Config()
#         notifier = WhatsAppNotifier(config)
#         timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
#         test_msg = (
#             f"*Teste de Integracao Evolution API*\n\n"
#             f"Conexao estabelecida com sucesso!\n"
#             f"Horario do teste: {timestamp}\n\n"
#             "O bot esta pronto para enviar notificacoes de reserva."
#         )
#         success = notifier.send_message(test_msg)
#         if success:
#             logger.info("TESTE CONCLUIDO COM SUCESSO!")
#             return True
#         logger.error("O teste falhou. Verifique os logs e sua API Key.")
#         return False
#     except ValueError as exc:
#         logger.error(f"Erro de configuracao: {exc}")
#         return False
#     except Exception as exc:
#         logger.exception(f"Ocorreu um erro inesperado: {exc}")
#         return False
#
# if __name__ == "__main__":
#     success = test_whatsapp_connection()
#     if not success:
#         sys.exit(1)
