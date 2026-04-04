import logging
logging.basicConfig(level=logging.DEBUG)

from datetime import date

from src.config import Config
from src.portal.client import create_browser
from src.portal.auth import login
from src.portal.availability import get_available_hours
from src.portal.reservation import execute_reservation

from src.reserva_bot.reservation_scheduler import plan_reservation

config = Config()
account = config.accounts[0]

target_date = date(2026, 4, 13)

with create_browser(headless=False) as (_, page):
    login(page, config, account["login"], account["password"])

    available_hours = get_available_hours(page, config, target_date)

    print("HORÁRIOS DISPONÍVEIS:", available_hours)

    plan = plan_reservation(
    available_hours=available_hours,
    accounts=[account],
    accepted_windows=config.accepted_windows,
    min_size=config.min_window_size,
    max_size=config.max_window_size,
)

    print("PLANO:", plan)

    if not plan:
        print("Nenhum bloco válido encontrado")
    else:
        chosen_hour = plan[0]["hour"]

        print("HORÁRIO ESCOLHIDO:", chosen_hour)

        sucesso = execute_reservation(page, chosen_hour)

        print("RESERVA:", sucesso)