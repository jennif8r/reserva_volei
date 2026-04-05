import json
import logging
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class StateStore:
    """
    Responsável por ler, consultar e salvar o estado local das reservas.
    """

    def __init__(self, file_path: str = "state.json") -> None:
        """
        Inicializa o repositório de estado.

        Args:
            file_path (str): Caminho do arquivo JSON de estado.
        """
        self.file_path = Path(file_path)
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """
        Carrega o estado do arquivo JSON.

        Returns:
            Dict[str, Any]: Estado carregado.
        """
        try:
            if not self.file_path.exists():
                logger.info(
                    "Arquivo de estado não encontrado. Criando estado inicial."
                )
                return {"reservations": []}

            content = self.file_path.read_text(encoding="utf-8").strip()

            if not content:
                logger.warning(
                    "Arquivo de estado vazio. Usando estrutura inicial."
                )
                return {"reservations": []}

            state = json.loads(content)

            if "reservations" not in state or not isinstance(
                state["reservations"],
                list,
            ):
                logger.warning(
                    "Estrutura inválida no estado. Reiniciando reservations."
                )
                state["reservations"] = []

            logger.info(
                "Estado carregado com %s reserva(s)",
                len(state["reservations"]),
            )
            return state

        except Exception:
            logger.exception("Erro ao carregar state.json")
            raise

    def save(self) -> None:
        """
        Salva o estado atual no arquivo JSON.
        """
        try:
            self.file_path.write_text(
                json.dumps(self.state, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            logger.info("Estado salvo com sucesso em %s", self.file_path)
        except Exception:
            logger.exception("Erro ao salvar state.json")
            raise

    def get_reservations(self) -> List[Dict[str, Any]]:
        """
        Retorna a lista de reservas registradas.

        Returns:
            List[Dict[str, Any]]: Lista de reservas.
        """
        return self.state.get("reservations", [])

    def get_account_id(self, account: Dict[str, Any]) -> str:
        """
        Retorna o identificador seguro da conta para uso no sistema e nos logs.

        Args:
            account (Dict[str, Any]): Conta carregada da configuração.

        Returns:
            str: Identificador da conta.
        """
        account_id = account.get("id", "").strip()

        if not account_id:
            raise ValueError("Conta sem campo 'id' válido.")

        return account_id

    def has_future_reservation(
        self,
        account_id: str,
        reference_date: date,
    ) -> bool:
        """
        Verifica se a conta já possui uma reserva futura ou atual.

        Args:
            account_id (str): ID da conta.
            reference_date (date): Data de referência.

        Returns:
            bool: True se já houver reserva futura ou atual.
        """
        try:
            for reservation in self.get_reservations():
                if reservation.get("account_id") != account_id:
                    continue

                reservation_date_str = reservation.get("date", "")
                reservation_status = reservation.get("status", "")

                if reservation_status != "confirmed":
                    continue

                if not reservation_date_str:
                    continue

                reservation_date = date.fromisoformat(reservation_date_str)

                if reservation_date >= reference_date:
                    logger.info(
                        "Conta %s já possui reserva futura em %s",
                        account_id,
                        reservation_date_str,
                    )
                    return True

            return False

        except Exception:
            logger.exception(
                "Erro ao verificar reserva futura da conta %s",
                account_id,
            )
            raise

    def add_reservation(
        self,
        account_id: str,
        reservation_date: date,
        hour: str,
        status: str = "confirmed",
    ) -> None:
        """
        Adiciona uma nova reserva ao estado e salva o arquivo.

        Args:
            account_id (str): ID da conta.
            reservation_date (date): Data da reserva.
            hour (str): Horário da reserva.
            status (str): Status da reserva.
        """
        try:
            record = {
                "account_id": account_id,
                "date": reservation_date.isoformat(),
                "hour": hour,
                "status": status,
            }

            self.state["reservations"].append(record)
            self.save()

            logger.info(
                "Reserva registrada para conta %s em %s às %s",
                account_id,
                reservation_date.isoformat(),
                hour,
            )
        except Exception:
            logger.exception(
                "Erro ao adicionar reserva da conta %s",
                account_id,
            )
            raise

    def get_reservation_for_account(
        self,
        account_id: str,
        reservation_date: Optional[date] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Retorna a reserva de uma conta, opcionalmente filtrando por data.

        Args:
            account_id (str): ID da conta.
            reservation_date (Optional[date]): Data específica.

        Returns:
            Optional[Dict[str, Any]]: Reserva encontrada ou None.
        """
        try:
            for reservation in self.get_reservations():
                if reservation.get("account_id") != account_id:
                    continue

                if reservation_date is not None:
                    if reservation.get("date") != reservation_date.isoformat():
                        continue

                return reservation

            return None

        except Exception:
            logger.exception(
                "Erro ao buscar reserva da conta %s",
                account_id,
            )
            raise

    def filter_available_accounts(
        self,
        accounts: List[Dict[str, Any]],
        reference_date: date,
    ) -> List[Dict[str, Any]]:
        """
        Filtra apenas as contas que ainda não possuem reserva futura.

        Args:
            accounts (List[Dict[str, Any]]): Lista de contas configuradas.
            reference_date (date): Data de referência.

        Returns:
            List[Dict[str, Any]]: Contas elegíveis para nova reserva.
        """
        try:
            available_accounts: List[Dict[str, Any]] = []

            for account in accounts:
                account_id = self.get_account_id(account)

                if self.has_future_reservation(account_id, reference_date):
                    logger.info(
                        "Conta %s foi removida da execução por já possuir reserva",
                        account_id,
                    )
                    continue

                available_accounts.append(account)

            logger.info(
                "%s conta(s) elegível(eis) para reserva",
                len(available_accounts),
            )
            return available_accounts

        except Exception:
            logger.exception("Erro ao filtrar contas elegíveis")
            raise