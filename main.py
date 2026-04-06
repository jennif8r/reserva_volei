import logging
from datetime import date, timedelta
from typing import List, Dict, Any

from src.config import Config
from src.portal.auth import login
from src.portal.availability import get_available_hours
from src.portal.client import create_browser
from src.portal.reservation import execute_reservation
from src.reserva_bot.reservation_scheduler import plan_reservation
from src.state_store import StateStore


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)

HEADLESS = True
SLOW_MO = 1800


def get_next_saturdays(limit: int = 4) -> List[date]:
    """
    Retorna os próximos N sábados a partir da data atual.

    Args:
        limit (int): Quantidade de sábados futuros.

    Returns:
        List[date]: Lista de datas.
    """
    today = date.today()
    days_ahead = (5 - today.weekday()) % 7

    if days_ahead == 0:
        days_ahead = 7

    first_saturday = today + timedelta(days=days_ahead)

    result = [
        first_saturday + timedelta(weeks=i)
        for i in range(limit)
    ]

    logger.debug("Sábados calculados: %s", result)

    return result


def build_safe_plan(plan: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Converte o plano em formato seguro para logs.

    Args:
        plan (List[Dict]): Plano de reserva.

    Returns:
        List[Dict]: Versão simplificada.
    """
    return [
        {
            "account_id": item["account"]["id"],
            "hour": item["hour"],
        }
        for item in plan
    ]


def fetch_available_hours(
    config: Config,
    account: Dict[str, Any],
    target_date: date,
) -> List[str]:
    """
    Busca horários disponíveis utilizando uma conta específica.
    """
    logger.info(
        "Consultando disponibilidade → conta=%s | data=%s",
        account["id"],
        target_date,
    )

    with create_browser(headless=HEADLESS, slow_mo=SLOW_MO) as (_, page):
        login(page, config, account["login"], account["password"])
        return get_available_hours(page, config, target_date)


def fetch_available_hours_resilient(
    config: Config,
    accounts: List[Dict[str, Any]],
    target_date: date,
) -> List[str]:
    """
    Tenta buscar horários usando múltiplas contas (fallback).

    Evita falha total caso uma conta não consiga logar.
    """
    for account in accounts:
        try:
            logger.debug(
                "Tentando buscar horários com conta %s",
                account["id"],
            )
            return fetch_available_hours(config, account, target_date)

        except Exception:
            logger.warning(
                "Falha ao buscar horários com conta %s",
                account["id"],
            )

    logger.error("Nenhuma conta conseguiu buscar horários")
    return []


def complete_window_if_possible(
    existing_reservations: List[Dict[str, Any]],
    available_hours: List[str],
    available_accounts: List[Dict[str, Any]],
    accepted_windows: List[List[str]],
) -> List[Dict[str, Any]] | None:
    """
    Tenta completar uma janela já parcialmente formada.

    Args:
        existing_reservations: Reservas existentes no dia.
        available_hours: Horários disponíveis no portal.
        available_accounts: Contas sem reserva.
        accepted_windows: Janelas válidas.

    Returns:
        Plano de reserva ou None.
    """
    existing_hours = [r["hour"] for r in existing_reservations]

    logger.debug("Horas já reservadas: %s", existing_hours)

    for window in accepted_windows:
        logger.debug("Testando janela: %s", window)

        if not set(existing_hours).issubset(set(window)):
            continue

        missing_hours = [
            h for h in window if h not in existing_hours
        ]

        logger.debug("Horas faltantes: %s", missing_hours)

        if not all(h in available_hours for h in missing_hours):
            continue

        if len(missing_hours) > len(available_accounts):
            continue

        logger.info("Janela completável encontrada: %s", window)

        return [
            {"account": acc, "hour": hour}
            for acc, hour in zip(available_accounts, missing_hours)
        ]

    return None


def execute_plan(
    config: Config,
    target_date: date,
    plan: List[Dict[str, Any]],
    state_store: StateStore,
) -> None:
    """
    Executa o plano de reservas no portal.
    """
    for item in plan:
        account = item["account"]
        account_id = account["id"]
        target_hour = item["hour"]

        logger.info(
            "Executando reserva → conta=%s | data=%s | hora=%s",
            account_id,
            target_date,
            target_hour,
        )

        try:
            with create_browser(headless=HEADLESS, slow_mo=SLOW_MO) as (_, page):

                login(page, config, account["login"], account["password"])

                available_hours = get_available_hours(
                    page,
                    config,
                    target_date,
                )

                if target_hour not in available_hours:
                    logger.warning(
                        "Horário não disponível → %s (%s)",
                        target_hour,
                        account_id,
                    )
                    continue

                success = execute_reservation(page, target_hour)

                if not success:
                    logger.warning(
                        "Falha ao reservar → conta=%s | hora=%s",
                        account_id,
                        target_hour,
                    )
                    continue

                state_store.add_reservation(
                    account_id=account_id,
                    reservation_date=target_date,
                    hour=target_hour,
                    status="confirmed",
                )

                logger.info(
                    "Reserva confirmada → conta=%s | %s %s",
                    account_id,
                    target_date,
                    target_hour,
                )

        except Exception:
            logger.exception(
                "Erro durante execução → conta=%s | hora=%s",
                account_id,
                target_hour,
            )


def main() -> None:
    """
    Fluxo principal do sistema de reservas.

    Para cada sábado:
        1. Analisa reservas existentes
        2. Busca horários disponíveis
        3. Tenta completar janela existente
        4. Caso não consiga, cria nova janela
        5. Executa reservas
    """
    try:
        config = Config()
        state_store = StateStore()

        target_dates = get_next_saturdays(limit=4)

        logger.info(
            "Próximos sábados: %s",
            [d.isoformat() for d in target_dates],
        )

        for target_date in target_dates:
            logger.info("==== PROCESSANDO %s ====", target_date)

            existing_reservations = state_store.get_reservations_by_date(
                target_date
            )

            reserved_ids = state_store.get_reserved_account_ids_by_date(
                target_date
            )

            logger.debug("Reservas existentes: %s", existing_reservations)

            available_accounts = [
                acc for acc in config.accounts
                if acc["id"] not in reserved_ids
            ]

            if not available_accounts:
                logger.info(
                    "Todas contas já possuem reserva para %s",
                    target_date,
                )
                continue

            logger.info(
                "Contas disponíveis: %s",
                [acc["id"] for acc in available_accounts],
            )

            available_hours = fetch_available_hours_resilient(
                config=config,
                accounts=config.accounts,
                target_date=target_date,
            )

            if not available_hours:
                logger.warning(
                    "Nenhum horário disponível para %s",
                    target_date,
                )
                continue

            logger.info("Horários disponíveis: %s", available_hours)

            plan = complete_window_if_possible(
                existing_reservations=existing_reservations,
                available_hours=available_hours,
                available_accounts=available_accounts,
                accepted_windows=config.accepted_windows,
            )

            # 🔁 fallback
            if not plan:
                logger.info("Usando planejamento padrão")

                plan = plan_reservation(
                    available_hours=available_hours,
                    accounts=available_accounts,
                    accepted_windows=config.accepted_windows,
                    min_size=config.min_window_size,
                    max_size=config.max_window_size,
                )

            if not plan:
                logger.warning(
                    "Nenhum plano possível para %s",
                    target_date,
                )
                continue

            logger.info("Plano final: %s", build_safe_plan(plan))

            execute_plan(
                config=config,
                target_date=target_date,
                plan=plan,
                state_store=state_store,
            )

    except Exception:
        logger.exception("Erro geral na execução")
        raise


if __name__ == "__main__":
    main()