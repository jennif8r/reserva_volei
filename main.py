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
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


HEADLESS = True
SLOW_MO = 1800


def get_next_saturdays(limit: int = 4) -> List[date]:
    """
    Retorna os próximos N sábados.
    """
    today = date.today()
    days_ahead = (5 - today.weekday()) % 7

    if days_ahead == 0:
        days_ahead = 7

    first_saturday = today + timedelta(days=days_ahead)

    return [
        first_saturday + timedelta(weeks=i)
        for i in range(limit)
    ]



def build_safe_plan(plan: List[Dict[str, Any]]) -> List[Dict[str, str]]:
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
    logger.info(
        "Consultando disponibilidade com conta %s para %s",
        account["id"],
        target_date.isoformat(),
    )

    with create_browser(headless=HEADLESS, slow_mo=SLOW_MO) as (_, page):
        login(page, config, account["login"], account["password"])
        return get_available_hours(page, config, target_date)



def execute_plan(
    config: Config,
    target_date: date,
    plan: List[Dict[str, Any]],
    state_store: StateStore,
) -> None:

    for item in plan:
        account = item["account"]
        account_id = account["id"]
        target_hour = item["hour"]

        logger.info(
            "Executando reserva → conta=%s | data=%s | hora=%s",
            account_id,
            target_date.isoformat(),
            target_hour,
        )

        try:
            with create_browser(headless=HEADLESS, slow_mo=SLOW_MO) as (_, page):

                login(page, config, account["login"], account["password"])

                available_hours = get_available_hours(page, config, target_date)

                if target_hour not in available_hours:
                    logger.warning(
                        "Horário %s não disponível para conta %s",
                        target_hour,
                        account_id,
                    )
                    continue

                success = execute_reservation(page, target_hour)

                if not success:
                    logger.warning(
                        "Falha ao reservar %s para conta %s",
                        target_hour,
                        account_id,
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
                    target_date.isoformat(),
                    target_hour,
                )

        except Exception:
            logger.exception(
                "Erro ao reservar conta=%s hora=%s",
                account_id,
                target_hour,
            )

def main() -> None:
    try:
        config = Config()
        state_store = StateStore()

        target_dates = get_next_saturdays(limit=4)

        logger.info("Próximos sábados: %s", [d.isoformat() for d in target_dates])

        # 🔁 percorre cada sábado
        for target_date in target_dates:

            logger.info("---- PROCESSANDO DATA %s ----", target_date.isoformat())

            eligible_accounts = state_store.filter_available_accounts(
                config.accounts,
                target_date,
            )

            if not eligible_accounts:
                logger.info("Todas contas já possuem reserva para %s", target_date)
                continue

            logger.info(
                "Contas elegíveis: %s",
                [acc["id"] for acc in eligible_accounts],
            )

            available_hours = fetch_available_hours(
                config=config,
                account=eligible_accounts[0],
                target_date=target_date,
            )

            if not available_hours:
                logger.warning("Nenhum horário disponível para %s", target_date)
                continue

            logger.info("Horários disponíveis: %s", available_hours)

            plan = plan_reservation(
                available_hours=available_hours,
                accounts=eligible_accounts,
                accepted_windows=config.accepted_windows,
                min_size=config.min_window_size,
                max_size=config.max_window_size,
            )

            if not plan:
                logger.warning("Nenhum plano válido para %s", target_date)
                continue

            logger.info("Plano: %s", build_safe_plan(plan))

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