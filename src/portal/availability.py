import logging
from datetime import date
from typing import List, Set

from playwright.sync_api import Page, TimeoutError

from src.config import Config

logger = logging.getLogger(__name__)


def open_new_reservation(page: Page) -> None:
    """
    Abre a tela de nova reserva.

    Args:
        page (Page): Página ativa do Playwright.
    """
    try:
        logger.debug("Abrindo nova reserva")
        page.locator("#btnNovaReserva").click()
        page.locator("#selectAtividade").wait_for(timeout=15000)
        logger.debug("Tela de nova reserva aberta com sucesso")
    except Exception:
        logger.exception("Erro ao abrir a tela de nova reserva")
        raise


def fill_reservation_form(page: Page, config: Config) -> None:
    """
    Preenche os campos principais do formulário de reserva.

    Args:
        page (Page): Página ativa do Playwright.
        config (Config): Configuração carregada do sistema.
    """
    try:
        logger.debug("Selecionando atividade: %s", config.activity_name)
        page.locator("#selectAtividade").select_option(label=config.activity_name)

        logger.debug("Selecionando regional: %s", config.regional_name)
        page.locator("#selectNucleo").select_option(label=config.regional_name)

        logger.debug("Selecionando unidade: %s", config.unit_name)
        page.locator("#selectUnidade").select_option(label=config.unit_name)

        logger.debug("Selecionando sugestão = Não")
        page.locator("#selectSugestao").select_option(label="Não")

        logger.debug("Preenchendo capacidade: %s", config.capacity)
        page.locator("#capacidadePessoas").fill(str(config.capacity))
        page.locator("#btnConfirmaCapacidade").click()

        logger.debug("Capacidade confirmada com sucesso")
    except Exception:
        logger.exception("Erro ao preencher formulário de reserva")
        raise


def set_reservation_date(page: Page, target_date: date) -> None:
    """
    Define a data da reserva no formulário.

    Args:
        page (Page): Página ativa do Playwright.
        target_date (date): Data alvo da consulta.
    """
    try:
        formatted_date = target_date.isoformat()
        logger.debug("Definindo data da reserva: %s", formatted_date)

        page.locator("#dataReferencia").wait_for(timeout=10000)

        page.evaluate(
            """
            (value) => {
                const input = document.getElementById("dataReferencia");
                input.value = value;
                input.dispatchEvent(new Event("input", { bubbles: true }));
                input.dispatchEvent(new Event("change", { bubbles: true }));
            }
            """,
            formatted_date,
        )

        page.locator("#btnConfirmaData").click()
        page.wait_for_timeout(3000)

        logger.debug("Data confirmada com sucesso")
    except Exception:
        logger.exception("Erro ao definir data da reserva")
        raise


def get_target_date_text(target_date: date) -> str:
    """
    Converte a data alvo para o formato exibido na página.

    Args:
        target_date (date): Data alvo.

    Returns:
        str: Data formatada como DD/MM/AAAA.
    """
    return target_date.strftime("%d/%m/%Y")


def load_more_results_until_target_date(
    page: Page,
    target_date_text: str,
    max_clicks: int = 10,
) -> None:
    """
    Clica em "Carregar mais" até encontrar a data alvo ou até o botão não estar mais disponível.

    Args:
        page (Page): Página ativa do Playwright.
        target_date_text (str): Data alvo no formato DD/MM/AAAA.
        max_clicks (int): Limite de cliques no botão.
    """
    try:
        logger.debug(
            "Tentando carregar mais resultados até encontrar a data %s",
            target_date_text,
        )

        for attempt in range(1, max_clicks + 1):
            if page.locator(f"span[data-dataagenda]:has-text('{target_date_text}')").count() > 0:
                logger.debug("Data alvo encontrada sem necessidade de mais cliques")
                return

            load_more_button = page.locator("#btnCarregarMais")

            if load_more_button.count() == 0:
                logger.debug("Botão 'Carregar mais' não encontrado")
                return

            if not load_more_button.is_visible():
                logger.debug("Botão 'Carregar mais' não está visível")
                return

            logger.debug(
                "Clicando em 'Carregar mais' (%s/%s)",
                attempt,
                max_clicks,
            )
            load_more_button.click()
            page.wait_for_timeout(1500)

        logger.debug(
            "Limite de cliques em 'Carregar mais' atingido sem confirmação da data alvo"
        )
    except TimeoutError:
        logger.warning("Timeout ao tentar carregar mais resultados")
    except Exception:
        logger.exception("Erro ao carregar mais resultados")
        raise


def get_result_blocks(page: Page) -> List:
    """
    Retorna os blocos de resultado disponíveis na tela.

    Args:
        page (Page): Página ativa do Playwright.

    Returns:
        List: Lista de locators de resultados.
    """
    blocks_locator = page.locator("div.resultado")
    count = blocks_locator.count()
    logger.debug("%s blocos de resultado encontrados", count)
    return [blocks_locator.nth(index) for index in range(count)]


def extract_hours_from_block(block) -> List[str]:
    """
    Extrai os horários visíveis de um bloco de resultado.

    Args:
        block: Locator do bloco de resultado.

    Returns:
        List[str]: Lista de horários encontrados no bloco.
    """
    hours_locator = block.locator("span[data-horarioagenda]:not(.d-none)")
    hours_count = hours_locator.count()

    hours: List[str] = []
    for index in range(hours_count):
        hour_text = hours_locator.nth(index).inner_text().strip()
        if hour_text:
            hours.append(hour_text)

    return hours


def extract_available_hours(
    page: Page,
    config: Config,
    target_date: date,
) -> List[str]:
    """
    Extrai os horários disponíveis para uma data específica.

    Args:
        page (Page): Página ativa do Playwright.
        config (Config): Configuração carregada do sistema.
        target_date (date): Data alvo da consulta.

    Returns:
        List[str]: Horários disponíveis, filtrados e ordenados.
    """
    try:
        logger.debug("Extraindo horários disponíveis")
        target_date_text = get_target_date_text(target_date)

        load_more_results_until_target_date(page, target_date_text)

        result_blocks = get_result_blocks(page)
        collected_hours: Set[str] = set()

        for block in result_blocks:
            date_locator = block.locator("span[data-dataagenda]")

            if date_locator.count() == 0:
                continue

            block_date_text = date_locator.first.inner_text().strip()

            if block_date_text != target_date_text:
                continue

            block_hours = extract_hours_from_block(block)

            if block_hours:
                logger.debug(
                    "Horários encontrados para %s: %s",
                    block_date_text,
                    block_hours,
                )

            for hour in block_hours:
                collected_hours.add(hour)

        if not collected_hours:
            logger.info(
                "Nenhum horário encontrado para a data %s",
                target_date_text,
            )
            return []

        filtered_hours = [
            hour
            for hour in config.target_hours
            if hour in collected_hours
        ]

        logger.info(
            "Horários disponíveis filtrados para %s: %s",
            target_date_text,
            filtered_hours,
        )
        return filtered_hours

    except Exception:
        logger.exception("Erro ao extrair horários disponíveis")

        try:
            page.screenshot(path="debug_availability.png", full_page=True)
            with open("debug_availability.html", "w", encoding="utf-8") as file:
                file.write(page.content())
            logger.error("Arquivos de debug salvos com sucesso")
        except Exception:
            logger.warning("Falha ao salvar arquivos de debug da disponibilidade")

        raise


def get_available_hours(
    page: Page,
    config: Config,
    target_date: date,
) -> List[str]:
    """
    Executa o fluxo completo para obter horários disponíveis para uma data.

    Args:
        page (Page): Página ativa do Playwright.
        config (Config): Configuração carregada do sistema.
        target_date (date): Data alvo da consulta.

    Returns:
        List[str]: Lista de horários disponíveis e aceitos pela configuração.
    """
    try:
        logger.info(
            "Consultando horários disponíveis para %s",
            target_date.strftime("%d/%m/%Y"),
        )

        open_new_reservation(page)
        fill_reservation_form(page, config)
        set_reservation_date(page, target_date)

        available_hours = extract_available_hours(
            page=page,
            config=config,
            target_date=target_date,
        )

        logger.info(
            "Consulta finalizada para %s com %s horário(s)",
            target_date.strftime("%d/%m/%Y"),
            len(available_hours),
        )
        return available_hours

    except Exception:
        logger.exception("Erro no fluxo completo de consulta de horários")
        raise