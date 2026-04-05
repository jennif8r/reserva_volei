import logging
import re
from typing import Optional

from playwright.sync_api import Page, TimeoutError

logger = logging.getLogger(__name__)


def wait_detail_loading(page: Page) -> None:
    """
    Aguarda um possível carregamento da tela de detalhes.

    Args:
        page (Page): Página ativa do Playwright.
    """
    loading_selectors = [
        ".loading",
        ".loader",
        ".spinner",
        ".spinner-border",
        ".spinner-grow",
        ".blockUI",
        "[aria-busy='true']",
    ]

    logger.debug("Aguardando possível carregamento da tela de detalhes")

    # pequena pausa para o carregamento começar
    page.wait_for_timeout(500)

    for selector in loading_selectors:
        try:
            locator = page.locator(selector).first
            if locator.count() > 0 and locator.is_visible():
                logger.debug("Loading detectado em %s", selector)
                locator.wait_for(state="hidden", timeout=15000)
                logger.debug("Loading finalizado em %s", selector)
                return
        except TimeoutError:
            logger.debug("Loading não sumiu a tempo para %s", selector)
        except Exception:
            continue

    try:
        page.wait_for_load_state("networkidle", timeout=5000)
    except TimeoutError:
        logger.debug("networkidle não foi atingido na tela de detalhes")


def wait_time_options_loaded(
    page: Page,
    target_hour: str,
    timeout_ms: int = 30000,
) -> None:
    """
    Aguarda o select de horários carregar opções reais.

    Regras:
        - o select precisa existir;
        - precisa haver opções válidas;
        - tenta aguardar até o horário alvo aparecer no texto das opções.

    Args:
        page (Page): Página ativa do Playwright.
        target_hour (str): Horário alvo no formato HH:MM.
        timeout_ms (int): Timeout em milissegundos.
    """
    logger.debug(
        "Aguardando carregamento das opções do select para o horário %s",
        target_hour,
    )

    page.locator("#selectHorario").wait_for(state="visible", timeout=15000)

    page.wait_for_function(
        """
        (targetHour) => {
            const select = document.querySelector("#selectHorario");
            if (!select) {
                return false;
            }

            const options = Array.from(select.options)
                .map(option => option.textContent.trim())
                .filter(text => text.length > 0);

            const validOptions = options.filter(text => {
                const lower = text.toLowerCase();
                return !lower.includes("selecione") && text.includes("às");
            });

            if (validOptions.length === 0) {
                return false;
            }

            return validOptions.some(text => text.startsWith(targetHour));
        }
        """,
        arg=target_hour,
        timeout=timeout_ms,
    )

    logger.debug("Opções do select carregadas com sucesso")

def click_hour_block(page: Page, target_hour: str) -> bool:
    """
    Clica em "Mais detalhes" no bloco que contém o horário desejado.

    Args:
        page (Page): Página ativa do Playwright.
        target_hour (str): Horário alvo no formato HH:MM.

    Returns:
        bool: True se encontrou e clicou no bloco; False caso contrário.
    """
    try:
        logger.debug("Procurando bloco com o horário %s", target_hour)

        result_blocks = page.locator("div.resultado")
        result_count = result_blocks.count()

        logger.debug("%s bloco(s) de resultado encontrado(s)", result_count)

        for block_index in range(result_count):
            block = result_blocks.nth(block_index)
            hour_elements = block.locator("span[data-horarioagenda]:not(.d-none)")
            hour_count = hour_elements.count()

            for hour_index in range(hour_count):
                block_hour = hour_elements.nth(hour_index).inner_text().strip()

                if block_hour == target_hour:
                    logger.info(
                        "Horário %s encontrado no bloco %s",
                        target_hour,
                        block_index,
                    )

                    details_button = block.locator("a:has-text('Mais detalhes')")
                    details_button.click()

                    wait_detail_loading(page)
                    wait_time_options_loaded(page, target_hour)

                    logger.debug("Tela de detalhes aberta com sucesso")
                    return True

        logger.warning("Nenhum bloco com o horário %s foi encontrado", target_hour)
        return False

    except Exception:
        logger.exception("Erro ao clicar no bloco do horário")
        return False


def parse_interval_start(interval_label: str) -> Optional[str]:
    """
    Extrai o horário inicial de um rótulo de intervalo.

    Exemplos:
        "16:00 às 17:00" -> "16:00"
        "16:00 às 16:59" -> "16:00"

    Args:
        interval_label (str): Texto do option.

    Returns:
        Optional[str]: Horário inicial ou None.
    """
    try:
        match = re.match(
            r"^\s*(\d{2}:\d{2})\s+às\s+\d{2}:\d{2}\s*$",
            interval_label,
        )
        if match:
            return match.group(1)
        return None
    except Exception:
        logger.exception("Erro ao interpretar o intervalo '%s'", interval_label)
        return None


def choose_best_interval(page: Page, target_hour: str) -> Optional[str]:
    """
    Escolhe o melhor intervalo para o horário desejado.

    Regra:
        1. Preferir intervalo cujo início seja exatamente igual ao target_hour.
        2. Se não existir, tentar fallback controlado.

    Args:
        page (Page): Página ativa do Playwright.
        target_hour (str): Horário alvo no formato HH:MM.

    Returns:
        Optional[str]: Label do intervalo escolhido ou None.
    """
    try:
        logger.debug("Lendo opções do select de horário para alvo %s", target_hour)

        option_elements = page.locator("#selectHorario option")
        option_count = option_elements.count()

        logger.debug("%s opção(ões) encontradas no select de horário", option_count)

        exact_match: Optional[str] = None
        safe_fallback: Optional[str] = None

        for index in range(option_count):
            label = option_elements.nth(index).inner_text().strip()

            if not label or label.lower().startswith("selecione"):
                continue

            start_hour = parse_interval_start(label)
            logger.debug(
                "Opção lida: '%s' | início interpretado: %s",
                label,
                start_hour,
            )

            if start_hour == target_hour:
                exact_match = label
                break

            if safe_fallback is None and re.search(
                rf"^{re.escape(target_hour)}\s+às\b",
                label,
            ):
                safe_fallback = label

        if exact_match:
            logger.info(
                "Intervalo exato encontrado para %s: %s",
                target_hour,
                exact_match,
            )
            return exact_match

        if safe_fallback:
            logger.warning(
                "Usando fallback para %s: %s",
                target_hour,
                safe_fallback,
            )
            return safe_fallback

        logger.warning("Nenhum intervalo compatível encontrado para %s", target_hour)
        return None

    except Exception:
        logger.exception("Erro ao escolher o melhor intervalo")
        return None


def select_time_slot(page: Page, target_hour: str) -> Optional[str]:
    """
    Seleciona o intervalo correto no dropdown de horários.

    Args:
        page (Page): Página ativa do Playwright.
        target_hour (str): Horário alvo no formato HH:MM.

    Returns:
        Optional[str]: Intervalo selecionado ou None.
    """
    try:
        logger.debug("Selecionando intervalo para o horário %s", target_hour)

        # reforço extra para garantir que as options já chegaram
        wait_time_options_loaded(page, target_hour)

        interval_label = choose_best_interval(page, target_hour)
        if not interval_label:
            return None

        page.locator("#selectHorario").select_option(label=interval_label)
        logger.info("Selecionando intervalo: %s", interval_label)

        page.locator("#linkConfirmacao").click()

        wait_detail_loading(page)
        page.locator("#checkResponsabilidade").wait_for(timeout=15000)

        logger.debug("Tela de confirmação aberta com sucesso")
        return interval_label

    except TimeoutError:
        logger.exception("Timeout ao selecionar o intervalo de horário")
        return None
    except Exception:
        logger.exception("Erro ao selecionar o intervalo de horário")
        return None


def confirm_reservation(page: Page) -> bool:
    """
    Confirma a reserva final.

    Args:
        page (Page): Página ativa do Playwright.

    Returns:
        bool: True em caso de sucesso; False caso contrário.
    """
    try:
        logger.debug("Confirmando reserva")

        responsibility_checkbox = page.locator("#checkResponsabilidade")
        responsibility_checkbox.scroll_into_view_if_needed()
        responsibility_checkbox.click()

        continue_button = page.locator("#btnContinuar")
        continue_button.click()

        wait_detail_loading(page)
        page.wait_for_timeout(6500)

        logger.info("Reserva confirmada com sucesso")
        return True

    except Exception:
        logger.exception("Erro ao confirmar a reserva")
        return False


def execute_reservation(page: Page, target_hour: str) -> bool:
    """
    Executa o fluxo completo de reserva para um horário específico.

    Args:
        page (Page): Página ativa do Playwright.
        target_hour (str): Horário desejado no formato HH:MM.

    Returns:
        bool: True em caso de sucesso; False caso contrário.
    """
    try:
        logger.info("Iniciando reserva para %s", target_hour)

        clicked = click_hour_block(page, target_hour)
        if not clicked:
            return False

        selected_interval = select_time_slot(page, target_hour)
        if not selected_interval:
            return False

        confirmed = confirm_reservation(page)
        if not confirmed:
            return False

        logger.info(
            "Reserva finalizada para %s com o intervalo '%s'",
            target_hour,
            selected_interval,
        )
        return True

    except Exception:
        logger.exception("Erro no fluxo completo de reserva")
        return False