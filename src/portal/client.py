import logging
from contextlib import contextmanager
from playwright.sync_api import sync_playwright, Browser, Page

logger = logging.getLogger(__name__)


@contextmanager
def create_browser(headless: bool = True, slow_mo: int = 0):
    """
    Cria um navegador Playwright com contexto seguro.

    Args:
        headless (bool): Executa sem interface gráfica.

    Yields:
        tuple(Browser, Page): Navegador e página ativa.
    """
    logger.info("Iniciando Playwright")

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(
                headless=headless,
                slow_mo=slow_mo, 
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                ]
            )

            context = browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )

            page = context.new_page()

            logger.info("Navegador iniciado com sucesso")

            yield browser, page

        except Exception:
            logger.exception("Erro ao iniciar navegador")
            raise

        finally:
            logger.info("Fechando navegador")
            try:
                browser.close()
            except Exception:
                logger.warning("Erro ao fechar navegador")