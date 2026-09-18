"""
Script de Teste Exclusivo da Reserva (Sem E-mail e Sem WhatsApp / Evolution API)

Fluxo executado:
1. Carrega configurações do portal e contas do .env (ignora notificações).
2. Abre o navegador visível (headless=False) para você acompanhar tudo na tela.
3. Efetua o login no portal com a primeira conta configurada.
4. Abre o questionário de reserva e preenche os dados.
5. Resolve o Captcha Altcha (seleciona o botão e aguarda a verificação).
6. Busca os horários disponíveis para o próximo sábado.
7. Se encontrar um horário disponível compatível com suas preferências:
   - Seleciona o horário ("Mais detalhes" -> select do intervalo).
   - Aceita o termo de responsabilidade.
   - Conclui a reserva com sucesso!
"""

import logging
import os
import sys
from datetime import date, timedelta
from typing import List

from src.config import Config
from src.portal.auth import login
from src.portal.availability import get_available_hours
from src.portal.client import create_browser
from src.portal.reservation import execute_reservation

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("teste_reserva")


def get_next_saturdays(limit: int = 4) -> List[date]:
    """Retorna os próximos N sábados."""
    today = date.today()
    days_ahead = (5 - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    first_saturday = today + timedelta(days=days_ahead)
    return [first_saturday + timedelta(weeks=i) for i in range(limit)]


def main():
    logger.info("==========================================================")
    logger.info("TESTE ISOLADO DO FLUXO DE RESERVA (SEM NOTIFICAÇÕES)")
    logger.info("==========================================================")

    try:
        config = Config()
    except Exception as e:
        logger.error("Erro ao carregar configurações: %s", e)
        logger.info("Verifique se o arquivo .env possui as variáveis básicas (URL, contas, atividade).")
        return

    if not config.accounts:
        logger.error("Nenhuma conta configurada em RESERVA_ACCOUNTS_JSON no .env.")
        return

    account = config.accounts[0]
    account_id = account.get("id", "Conta Principal")
    saturdays = get_next_saturdays(limit=config.lookahead_weeks or 4)

    # HEADLESS configurável via variável de ambiente ou falso por padrão para teste visual
    headless = os.getenv("HEADLESS", "false").lower() in ("true", "1", "yes")
    slow_mo = int(os.getenv("SLOW_MO", "1000"))

    logger.info("Conta ativa para teste: %s (login: %s)", account_id, account["login"])
    logger.info("Modo gráfico: %s (slow_mo: %sms)", "Sem interface (headless)" if headless else "Visível na tela", slow_mo)
    logger.info("Sábados que serão consultados: %s", [s.strftime("%d/%m/%Y") for s in saturdays])

    with create_browser(headless=headless, slow_mo=slow_mo) as (_, page):
        try:
            # 1. Login
            logger.info(">>> PASSO 1: Realizando login no portal...")
            login(page, config, account["login"], account["password"])
            logger.info(">>> Login concluído com sucesso!")

            reserva_realizada = False

            # 2. Testa cada sábado até encontrar horários e tentar a reserva
            for target_date in saturdays:
                target_date_str = target_date.strftime("%d/%m/%Y")
                logger.info("----------------------------------------------------------")
                logger.info(">>> PASSO 2: Consultando disponibilidade para %s...", target_date_str)

                available_hours = get_available_hours(page, config, target_date)
                logger.info("Horários disponíveis retornados: %s", available_hours)

                if not available_hours:
                    logger.info("Nenhum horário disponível para %s. Verificando próximo sábado...", target_date_str)
                    continue

                # Escolhe o primeiro horário disponível que esteja nos target_hours (ou o primeiro da lista)
                chosen_hour = None
                for hour in config.target_hours:
                    if hour in available_hours:
                        chosen_hour = hour
                        break

                if not chosen_hour:
                    chosen_hour = available_hours[0]

                logger.info(">>> PASSO 3: Horário selecionado para testar reserva: %s", chosen_hour)
                logger.info(">>> PASSO 4: Executando fluxo de reserva no portal...")

                success = execute_reservation(page, chosen_hour)

                if success:
                    logger.info("==========================================================")
                    logger.info("🎉 RESERVA TESTADA E CONFIRMADA COM SUCESSO!")
                    logger.info("📅 Data: %s", target_date_str)
                    logger.info("⏰ Horário: %s", chosen_hour)
                    logger.info("👤 Conta: %s", account_id)
                    logger.info("==========================================================")
                    reserva_realizada = True
                    break
                else:
                    logger.warning("Falha ao tentar reservar o horário %s em %s.", chosen_hour, target_date_str)

            if not reserva_realizada:
                logger.info("Nenhum sábado com horários disponíveis para efetuar a reserva no momento.")

        except Exception:
            logger.exception("Erro durante a execução do teste de reserva")


if __name__ == "__main__":
    main()
