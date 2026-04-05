import logging
from pathlib import Path
from typing import List, Optional

from playwright.sync_api import Page, TimeoutError

from src.config import Config

logger = logging.getLogger(__name__)

DEBUG_DIR = Path("artifacts")
DEBUG_DIR.mkdir(exist_ok=True)


def save_login_debug(page: Page) -> None:
    """
    Salva screenshot e HTML para depuração do fluxo de login.

    Args:
        page (Page): Página ativa do Playwright.
    """
    try:
        screenshot_path = DEBUG_DIR / "debug_login.png"
        html_path = DEBUG_DIR / "debug_login.html"

        page.screenshot(path=str(screenshot_path), full_page=True)
        html_path.write_text(page.content(), encoding="utf-8")

        logger.error(
            "Arquivos de debug salvos: %s e %s",
            screenshot_path,
            html_path,
        )
    except Exception:
        logger.warning("Falha ao salvar arquivos de debug do login", exc_info=True)


def get_visible_error_text(page: Page) -> Optional[str]:
    """
    Tenta extrair uma mensagem de erro visível da tela de login.

    Args:
        page (Page): Página ativa do Playwright.

    Returns:
        Optional[str]: Texto de erro encontrado, se existir.
    """
    possible_selectors: List[str] = [
        "#msgErro",
        ".validation-summary-errors",
        ".text-danger",
        ".alert-danger",
        ".alert-warning",
        "[role='alert']",
    ]

    for selector in possible_selectors:
        try:
            locator = page.locator(selector).first
            if locator.count() > 0 and locator.is_visible():
                text = locator.inner_text().strip()
                if text:
                    return text
        except Exception:
            continue

    return None


def wait_login_button_enabled(page: Page, timeout_ms: int = 30000) -> None:
    """
    Aguarda o botão de login ficar habilitado.

    Args:
        page (Page): Página ativa do Playwright.
        timeout_ms (int): Timeout em milissegundos.
    """
    page.wait_for_function(
        """
        () => {
            const button = document.querySelector("#btnSenhaProximo");
            return !!button && !button.disabled;
        }
        """,
        timeout=timeout_ms,
    )


def wait_loading_after_login_click(page: Page) -> None:
    """
    Aguarda um possível ciclo de carregamento após clicar no botão de login.

    Observação:
        Como o seletor exato do loading pode variar, a função tenta detectar
        padrões comuns. Se não encontrar nada, segue o fluxo normalmente.

    Args:
        page (Page): Página ativa do Playwright.
    """
    loading_selectors = [
        ".loading",
        ".loader",
        ".spinner",
        ".spinner-border",
        ".spinner-grow",
        ".aguarde",
        "[aria-busy='true']",
        ".blockUI",
    ]

    try:
        logger.debug("Aguardando possível carregamento pós-login")

        # pequena pausa para o JS do site iniciar o loading
        page.wait_for_timeout(1200)

        for selector in loading_selectors:
            locator = page.locator(selector).first
            try:
                if locator.count() > 0 and locator.is_visible():
                    logger.debug("Loading detectado em %s", selector)
                    locator.wait_for(state="hidden", timeout=30000)
                    logger.debug("Loading finalizado em %s", selector)
                    return
            except TimeoutError:
                logger.debug("Loading não sumiu a tempo para %s", selector)
            except Exception:
                continue

        # fallback: aguarda estados gerais
        try:
            page.wait_for_load_state("domcontentloaded", timeout=10000)
        except TimeoutError:
            pass

        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except TimeoutError:
            logger.debug("networkidle não foi atingido após o login")

    except Exception:
        logger.warning(
            "Falha ao aguardar carregamento pós-login",
            exc_info=True,
        )


def wait_for_post_login(page: Page, timeout_ms: int = 60000) -> None:
    """
    Aguarda sinais de sucesso após o login.

    Args:
        page (Page): Página ativa do Playwright.
        timeout_ms (int): Timeout total em milissegundos.
    """
    logger.debug("Aguardando conclusão do login")

    success_selectors = [
        "#btnNovaReserva",
        "text=Nova Reserva",
        "#selectAtividade",
        "#containerQuestionario",
    ]

    end_time = page.evaluate("Date.now()") + timeout_ms

    while True:
        for selector in success_selectors:
            try:
                locator = page.locator(selector).first
                if locator.count() > 0 and locator.is_visible():
                    logger.info(
                        "Login concluído com sucesso via seletor %s",
                        selector,
                    )
                    return
            except Exception:
                continue

        visible_error = get_visible_error_text(page)
        if visible_error:
            raise RuntimeError(
                f"Erro exibido pela página após login: {visible_error}"
            )

        now = page.evaluate("Date.now()")
        if now >= end_time:
            break

        page.wait_for_timeout(500)

    raise TimeoutError(
        f"Falha ao identificar sucesso no login após {timeout_ms}ms"
    )


def submit_login(page: Page) -> None:
    """
    Executa o submit do login de forma robusta.

    Args:
        page (Page): Página ativa do Playwright.
    """
    password_input = page.locator("#senha")
    login_button = page.locator("#btnSenhaProximo")

    logger.debug("Forçando blur no campo de senha")
    password_input.press("Tab")

    # importante: deixa o front processar a senha antes do clique
    logger.debug("Aguardando processamento da senha")
    page.wait_for_timeout(3500)

    logger.debug("Aguardando botão de login habilitar")
    wait_login_button_enabled(page, timeout_ms=30000)

    for attempt in range(1, 4):
        try:
            logger.debug("Tentativa %s de clicar no botão de login", attempt)
            login_button.click(timeout=10000)
            wait_loading_after_login_click(page)
            return
        except Exception:
            logger.warning(
                "Falha ao clicar no botão de login na tentativa %s",
                attempt,
                exc_info=True,
            )

            if attempt == 2:
                try:
                    logger.debug("Tentando fallback com click via JavaScript")
                    page.evaluate(
                        """
                        () => {
                            const button = document.querySelector("#btnSenhaProximo");
                            if (button) {
                                button.click();
                            }
                        }
                        """
                    )
                    wait_loading_after_login_click(page)
                    return
                except Exception:
                    logger.warning(
                        "Fallback via JavaScript falhou",
                        exc_info=True,
                    )

            if attempt == 3:
                raise

            page.wait_for_timeout(2000)


def login(
    page: Page,
    config: Config,
    login_value: str,
    password: str,
) -> None:
    """
    Realiza login no portal.

    Args:
        page (Page): Página do Playwright.
        config (Config): Configuração do sistema.
        login_value (str): CPF ou login.
        password (str): Senha da conta.
    """
    try:
        logger.info("Acessando portal")
        page.goto(config.url, wait_until="domcontentloaded")
        page.set_default_timeout(60000)

        try:
            logger.debug("Tentando fechar popup inicial")
            page.locator("#btn-fechar-popup").click(timeout=6000)
            logger.debug("Popup fechado")
        except TimeoutError:
            logger.debug("Popup não apareceu")

        logger.debug("Clicando em Portal")
        page.locator("#btnPortal").click()

        logger.debug("Selecionando login com CPF")
        page.get_by_role("button", name="Entrar com CPF").click()

        logger.debug("Aguardando campo de CPF")
        page.locator("#documento").wait_for(state="visible", timeout=15000)

        logger.debug("Preenchendo CPF")
        page.locator("#documento").fill(login_value)
        page.locator("#btnProximo").click()

        logger.debug("Aguardando campo de senha")
        page.locator("#senha").wait_for(state="visible", timeout=15000)

        logger.debug("Preenchendo senha")
        page.locator("#senha").fill(password)

        submit_login(page)
        wait_for_post_login(page, timeout_ms=60000)

        logger.info("Login realizado com sucesso")

    except Exception:
        logger.exception("Erro durante login")
        save_login_debug(page)
        raise