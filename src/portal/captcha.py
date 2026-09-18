import logging
from playwright.sync_api import Page, TimeoutError

logger = logging.getLogger(__name__)


def _is_altcha_verified(page: Page) -> bool:
    """
    Verifica se o widget Altcha já se encontra no estado 'verified' ou se o
    input oculto já contém o token gerado.

    Args:
        page (Page): Página ativa do Playwright.

    Returns:
        bool: True se já estiver verificado, False caso contrário.
    """
    try:
        return bool(
            page.evaluate(
                """
                () => {
                    const widget = document.querySelector('#altchaWidget') || document.querySelector('altcha-widget');
                    if (!widget) return false;
                    const root = widget.shadowRoot || widget;
                    const stateEl = root.querySelector('.altcha');
                    if (stateEl && stateEl.getAttribute('data-state') === 'verified') return true;
                    const hiddenInput = root.querySelector('input[name="altcha"]') || widget.querySelector('input[name="altcha"]');
                    return !!(hiddenInput && hiddenInput.value);
                }
                """
            )
        )
    except Exception:
        return False


def handle_altcha_captcha(
    page: Page,
    timeout_ms: int = 30000,
    max_attempts: int = 2,
) -> None:
    """
    Identifica e resolve o captcha Altcha (PoW) selecionando o botão/checkbox
    e aguardando o processamento até atingir o estado 'verified'.

    Args:
        page (Page): Página ativa do Playwright.
        timeout_ms (int): Timeout máximo em ms para aguardar a resolução.
        max_attempts (int): Número máximo de tentativas caso ocorra erro.
    """
    try:
        logger.debug("Verificando presença do captcha Altcha (#altchaWidget)")
        widget = page.locator("#altchaWidget, altcha-widget").first

        try:
            widget.wait_for(state="attached", timeout=5000)
        except TimeoutError:
            logger.debug("Widget de captcha (#altchaWidget) não detectado na página.")
            return

        try:
            widget.scroll_into_view_if_needed()
        except Exception:
            pass

        if _is_altcha_verified(page):
            logger.info("Captcha Altcha já se encontra verificado.")
            return

        for attempt in range(1, max_attempts + 1):
            logger.info(
                "Selecionando botão do captcha Altcha (tentativa %s/%s)...",
                attempt,
                max_attempts,
            )

            clicked = False

            # 1. Tenta clicar na label visível ("Não sou um robô")
            label = page.locator(
                "#altchaWidget label, altcha-widget label, #altchaWidget .altcha-label"
            ).first
            if label.count() > 0 and label.is_visible():
                try:
                    logger.debug("Clicando na label do captcha")
                    label.click(timeout=3000)
                    clicked = True
                except Exception:
                    logger.debug("Falha ao clicar na label do captcha via locator")

            # 2. Se não clicou pela label, tenta o checkbox diretamente
            if not clicked:
                checkbox = page.locator(
                    "#altchaWidget input[type='checkbox'], altcha-widget input[type='checkbox']"
                ).first
                if checkbox.count() > 0:
                    try:
                        logger.debug("Clicando no checkbox do captcha")
                        checkbox.click(timeout=3000)
                        clicked = True
                    except Exception:
                        try:
                            logger.debug("Tentando check forçado no checkbox")
                            checkbox.check(force=True, timeout=3000)
                            clicked = True
                        except Exception:
                            logger.debug("Falha ao clicar/marcar checkbox do captcha")

            # 3. Fallback via JavaScript caso o clique Playwright tenha falhado
            if not clicked:
                logger.debug("Tentando acionar captcha via JavaScript (evaluate)")
                try:
                    page.evaluate(
                        """
                        () => {
                            const widget = document.querySelector('#altchaWidget') || document.querySelector('altcha-widget');
                            if (!widget) return;
                            const root = widget.shadowRoot || widget;
                            const cb = root.querySelector("input[type='checkbox']");
                            if (cb) {
                                cb.click();
                            } else {
                                const lbl = root.querySelector("label");
                                if (lbl) lbl.click();
                            }
                        }
                        """
                    )
                    clicked = True
                except Exception:
                    logger.warning("Falha ao acionar captcha via JavaScript", exc_info=True)

            logger.debug("Aguardando verificação do captcha Altcha...")
            single_timeout = max(5000, timeout_ms // max_attempts)

            try:
                page.wait_for_function(
                    """
                    () => {
                        const widget = document.querySelector('#altchaWidget') || document.querySelector('altcha-widget');
                        if (!widget) return true;
                        const root = widget.shadowRoot || widget;
                        const stateEl = root.querySelector('.altcha');
                        if (stateEl) {
                            const state = stateEl.getAttribute('data-state');
                            if (state === 'verified') return true;
                            if (state === 'error') return true; // sai para retry
                        }
                        const hiddenInput = root.querySelector('input[name="altcha"]') || widget.querySelector('input[name="altcha"]');
                        if (hiddenInput && hiddenInput.value) return true;
                        return false;
                    }
                    """,
                    timeout=single_timeout,
                )

                if _is_altcha_verified(page):
                    logger.info("Captcha Altcha verificado com sucesso!")
                    page.wait_for_timeout(500)
                    return
                else:
                    logger.warning(
                        "Captcha Altcha retornou erro na tentativa %s. Aguardando para nova tentativa...",
                        attempt,
                    )
                    page.wait_for_timeout(1000)

            except TimeoutError:
                logger.warning(
                    "Timeout aguardando verificação do captcha na tentativa %s",
                    attempt,
                )

        if _is_altcha_verified(page):
            logger.info("Captcha Altcha verificado com sucesso!")
            return

        raise TimeoutError(
            f"Captcha Altcha não foi verificado após {max_attempts} tentativa(s)."
        )

    except Exception:
        logger.exception("Erro ao manipular captcha Altcha")
        raise
