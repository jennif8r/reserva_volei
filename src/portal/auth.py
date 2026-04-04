import logging
from playwright.sync_api import Page, TimeoutError

from src.config import Config

logger = logging.getLogger(__name__)


def login(
    page: Page,
    config: Config,
    login_value: str,
    password: str
) -> None:
    """
    Realiza login no portal Curitiba em Movimento.

    Fluxo:
        1. Acessa portal
        2. Fecha popup (se existir)
        3. Clica em "Portal"
        4. Seleciona login com CPF
        5. Preenche CPF
        6. Preenche senha
        7. Aguarda área logada

    Args:
        page (Page): Página do Playwright.
        config (Config): Configuração do sistema.
        login_value (str): CPF/login.
        password (str): Senha.
    """
    try:
        logger.info("Acessando portal")
        page.goto(config.url, wait_until="domcontentloaded")

        page.set_default_timeout(20000)

        try:
            logger.debug("Tentando fechar popup inicial")
            page.locator("#btn-fechar-popup").click(timeout=3000)
            logger.debug("Popup fechado")
        except TimeoutError:
            logger.debug("Popup não apareceu")

        logger.debug("Clicando em Portal")
        page.locator("#btnPortal").click()

        logger.debug("Selecionando login com CPF")
        page.get_by_role("button", name="Entrar com CPF").click()

        logger.debug("Aguardando campo de CPF")
        page.locator("#documento").wait_for()

        logger.debug("Preenchendo CPF")
        page.locator("#documento").fill(login_value)

        page.locator("#btnProximo").click()

        logger.debug("Aguardando campo de senha")
        page.locator("#senha").wait_for()

        logger.debug("Preenchendo senha")
        page.locator("#senha").fill(password)

        page.locator("#btnSenhaProximo").click()

        logger.debug("Aguardando botão 'Nova Reserva'")
        page.locator("#btnNovaReserva").wait_for(timeout=15000)

        logger.info("Login realizado com sucesso")

    except Exception:
        logger.exception("Erro durante login")

        try:
            page.screenshot(path="debug_login.png")
            with open("debug_login.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            logger.error("Screenshot e HTML salvos para debug")
        except Exception:
            logger.warning("Falha ao salvar debug")

        raise