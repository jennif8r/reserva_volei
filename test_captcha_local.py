"""
Script de Teste Local: Validação Visual do Captcha e Questionário

Executa o fluxo de login e consulta de horários abrindo a janela do navegador
(headless=False) para que você possa acompanhar o bot preenchendo o questionário
e selecionando o Captcha Altcha automaticamente.

NÃO REALIZA NENHUMA RESERVA FINAL.
"""

import logging
from datetime import date, timedelta
from src.config import Config
from src.portal.auth import login
from src.portal.availability import get_available_hours
from src.portal.client import create_browser

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("teste_local")


def get_next_saturday() -> date:
    today = date.today()
    days_ahead = (5 - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return today + timedelta(days=days_ahead)


def main():
    logger.info("Iniciando teste visual local do captcha e questionário...")

    try:
        config = Config()
    except Exception as e:
        logger.error("Erro ao carregar configurações do .env: %s", e)
        logger.info("Certifique-se de que o arquivo .env existe na raiz com todas as variáveis preenchidas.")
        return

    if not config.accounts:
        logger.error("Nenhuma conta configurada em RESERVA_ACCOUNTS_JSON.")
        return

    account = config.accounts[0]
    target_date = get_next_saturday()

    logger.info("Utilizando conta de teste: %s", account["id"])
    logger.info("Consultando sábado alvo: %s", target_date.strftime("%d/%m/%Y"))

    # Abre o navegador visível com delay de 1s entre ações para acompanhar na tela
    with create_browser(headless=False, slow_mo=1000) as (_, page):
        try:
            logger.info("1. Realizando login...")
            login(page, config, account["login"], account["password"])
            logger.info("Login realizado com sucesso!")

            logger.info("2. Navegando para o questionário e resolvendo Captcha Altcha...")
            hours = get_available_hours(page, config, target_date)

            logger.info("==================================================")
            logger.info("TESTE CONCLUÍDO COM SUCESSO!")
            logger.info("Captcha resolvido e busca efetuada com sucesso.")
            logger.info("Horários disponíveis encontrados para %s: %s", target_date.strftime("%d/%m/%Y"), hours)
            logger.info("==================================================")

        except Exception:
            logger.exception("Falha durante o teste local")


if __name__ == "__main__":
    main()
