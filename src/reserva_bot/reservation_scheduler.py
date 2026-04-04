import logging
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def get_next_saturdays(weeks_ahead: int) -> List[date]:
    """
    Retorna uma lista com os próximos sábados.

    Args:
        weeks_ahead (int): Quantidade de semanas futuras a considerar.

    Returns:
        List[date]: Lista de sábados futuros.
    """
    try:
        logger.debug(
            "Calculando próximos sábados para %s semana(s)",
            weeks_ahead,
        )

        today = date.today()
        saturdays: List[date] = []

        for day_offset in range(1, weeks_ahead * 7 + 1):
            current_day = today + timedelta(days=day_offset)
            if current_day.weekday() == 5:
                saturdays.append(current_day)

        logger.info("%s sábado(s) encontrado(s)", len(saturdays))
        return saturdays

    except Exception:
        logger.exception("Erro ao calcular próximos sábados")
        raise


def normalize_hours(hours: List[str]) -> List[str]:
    """
    Normaliza e ordena horários no formato HH:MM.

    Args:
        hours (List[str]): Lista de horários.

    Returns:
        List[str]: Lista ordenada e sem duplicidade.
    """
    try:
        normalized = sorted(set(hour.strip() for hour in hours if hour.strip()))
        logger.debug("Horários normalizados: %s", normalized)
        return normalized
    except Exception:
        logger.exception("Erro ao normalizar horários")
        raise


def is_window_available(
    available_hours: List[str],
    window: List[str],
) -> bool:
    """
    Verifica se todos os horários de uma janela estão disponíveis.

    Args:
        available_hours (List[str]): Horários disponíveis.
        window (List[str]): Janela candidata.

    Returns:
        bool: True se a janela inteira estiver disponível.
    """
    try:
        available_set = set(available_hours)
        result = all(hour in available_set for hour in window)

        logger.debug(
            "Janela %s %s disponível",
            window,
            "está" if result else "não está",
        )
        return result

    except Exception:
        logger.exception("Erro ao verificar disponibilidade da janela")
        raise


def filter_candidate_windows(
    available_hours: List[str],
    accepted_windows: List[List[str]],
    min_size: int,
    max_size: int,
) -> List[List[str]]:
    """
    Filtra janelas aceitas que cabem dentro dos horários disponíveis.

    Args:
        available_hours (List[str]): Horários disponíveis.
        accepted_windows (List[List[str]]): Janelas aceitas em ordem de prioridade.
        min_size (int): Tamanho mínimo permitido.
        max_size (int): Tamanho máximo permitido.

    Returns:
        List[List[str]]: Janelas candidatas válidas.
    """
    try:
        logger.debug(
            "Filtrando janelas candidatas com min=%s, max=%s",
            min_size,
            max_size,
        )

        normalized_hours = normalize_hours(available_hours)
        candidate_windows: List[List[str]] = []

        for window in accepted_windows:
            if not (min_size <= len(window) <= max_size):
                logger.debug(
                    "Janela ignorada por tamanho fora da regra: %s",
                    window,
                )
                continue

            if is_window_available(normalized_hours, window):
                candidate_windows.append(window)

        logger.info(
            "%s janela(s) candidata(s) encontrada(s): %s",
            len(candidate_windows),
            candidate_windows,
        )
        return candidate_windows

    except Exception:
        logger.exception("Erro ao filtrar janelas candidatas")
        raise


def pick_best_window(
    candidate_windows: List[List[str]],
) -> Optional[List[str]]:
    """
    Seleciona a melhor janela conforme a ordem já definida na configuração.

    A prioridade é a ordem do ACCEPTED_WINDOWS_JSON.

    Args:
        candidate_windows (List[List[str]]): Janelas candidatas válidas.

    Returns:
        Optional[List[str]]: Melhor janela ou None.
    """
    try:
        if not candidate_windows:
            logger.warning("Nenhuma janela candidata disponível")
            return None

        best_window = candidate_windows[0]
        logger.info("Janela escolhida: %s", best_window)
        return best_window

    except Exception:
        logger.exception("Erro ao selecionar melhor janela")
        raise


def assign_accounts_to_window(
    accounts: List[Any],
    window: List[str],
) -> List[Dict[str, Any]]:
    """
    Distribui contas nos horários da janela escolhida.

    Args:
        accounts (List[Any]): Lista de contas elegíveis.
        window (List[str]): Janela escolhida.

    Returns:
        List[Dict[str, Any]]: Plano de reserva conta-horário.
    """
    try:
        assignments: List[Dict[str, Any]] = []

        for account, hour in zip(accounts, window):
            assignments.append(
                {
                    "account": account,
                    "hour": hour,
                }
            )

        logger.info(
            "%s conta(s) distribuída(s): %s",
            len(assignments),
            assignments,
        )
        return assignments

    except Exception:
        logger.exception("Erro ao distribuir contas na janela")
        raise


def plan_reservation(
    available_hours: List[str],
    accounts: List[Any],
    accepted_windows: List[List[str]],
    min_size: int,
    max_size: int,
) -> Optional[List[Dict[str, Any]]]:
    """
    Planeja a reserva com base nos horários disponíveis e nas janelas aceitas.

    Regras:
        1. Filtra pelos horários disponíveis
        2. Verifica quais janelas aceitas cabem nesses horários
        3. Escolhe a primeira janela válida da lista
        4. Distribui as contas em sequência

    Args:
        available_hours (List[str]): Horários disponíveis.
        accounts (List[Any]): Contas disponíveis para reservar.
        accepted_windows (List[List[str]]): Janelas aceitas, em ordem de prioridade.
        min_size (int): Tamanho mínimo permitido para a janela.
        max_size (int): Tamanho máximo permitido para a janela.

    Returns:
        Optional[List[Dict[str, Any]]]: Plano de reserva ou None.
    """
    try:
        logger.info("Iniciando planejamento de reserva")

        if not available_hours:
            logger.warning("Nenhum horário disponível")
            return None

        if not accounts:
            logger.warning("Nenhuma conta disponível")
            return None

        candidate_windows = filter_candidate_windows(
            available_hours=available_hours,
            accepted_windows=accepted_windows,
            min_size=min_size,
            max_size=max_size,
        )

        if not candidate_windows:
            logger.warning("Nenhuma janela válida encontrada")
            return None

        best_window = pick_best_window(candidate_windows)

        if not best_window:
            logger.warning("Falha ao selecionar janela")
            return None

        result = assign_accounts_to_window(accounts, best_window)

        logger.info("Planejamento concluído com sucesso")
        return result

    except Exception:
        logger.exception("Erro no planejamento de reserva")
        raise