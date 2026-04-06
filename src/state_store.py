import json
import logging
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class StateStore:
    """
    Classe responsável por gerenciar o estado local das reservas.

    Este estado é persistido em um arquivo JSON e contém todas as reservas
    já realizadas, permitindo ao sistema tomar decisões inteligentes
    com base no histórico.
    """

    def __init__(self, file_path: str = "state.json") -> None:
        """
        Inicializa o StateStore carregando o estado do arquivo.

        Args:
            file_path (str): Caminho para o arquivo JSON de estado.
        """
        logger.debug("Inicializando StateStore com arquivo: %s", file_path)

        self.file_path = Path(file_path)
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """
        Carrega o estado do arquivo JSON.

        Returns:
            Dict[str, Any]: Estrutura de estado carregada.
        """
        try:
            if not self.file_path.exists():
                logger.info(
                    "Arquivo de estado não encontrado. Criando estrutura inicial."
                )
                return {"reservations": []}

            content = self.file_path.read_text(encoding="utf-8").strip()

            if not content:
                logger.warning(
                    "Arquivo de estado está vazio. Inicializando estrutura padrão."
                )
                return {"reservations": []}

            state = json.loads(content)

            if "reservations" not in state or not isinstance(
                state["reservations"], list
            ):
                logger.warning(
                    "Estrutura inválida detectada. Resetando lista de reservas."
                )
                state["reservations"] = []

            logger.info(
                "Estado carregado com %d reserva(s)",
                len(state["reservations"]),
            )

            logger.debug("Conteúdo do estado carregado: %s", state)

            return state

        except Exception:
            logger.exception("Erro ao carregar arquivo de estado")
            raise

    def save(self) -> None:
        """
        Persiste o estado atual no arquivo JSON.
        """
        try:
            logger.debug("Salvando estado atual no arquivo")

            self.file_path.write_text(
                json.dumps(self.state, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            logger.info("Estado salvo com sucesso em %s", self.file_path)

        except Exception:
            logger.exception("Erro ao salvar o estado")
            raise

    def get_reservations(self) -> List[Dict[str, Any]]:
        """
        Retorna todas as reservas armazenadas.

        Returns:
            List[Dict[str, Any]]: Lista de reservas.
        """
        reservations = self.state.get("reservations", [])

        logger.debug("Total de reservas retornadas: %d", len(reservations))

        return reservations

    def get_account_id(self, account: Dict[str, Any]) -> str:
        """
        Extrai e valida o ID de uma conta.

        Args:
            account (Dict[str, Any]): Dados da conta.

        Returns:
            str: ID da conta validado.

        Raises:
            ValueError: Se o ID estiver ausente ou inválido.
        """
        account_id = account.get("id", "").strip()

        logger.debug("Extraindo account_id: %s", account_id)

        if not account_id:
            raise ValueError("Conta sem campo 'id' válido.")

        return account_id


    def get_reservations_by_date(
        self, target_date: date
    ) -> List[Dict[str, Any]]:
        """
        Retorna todas as reservas confirmadas para uma data específica.

        Args:
            target_date (date): Data alvo.

        Returns:
            List[Dict[str, Any]]: Lista de reservas na data.
        """
        try:
            logger.debug("Buscando reservas para a data: %s", target_date)

            result = [
                r
                for r in self.get_reservations()
                if r.get("date") == target_date.isoformat()
                and r.get("status") == "confirmed"
            ]

            logger.debug("Reservas encontradas: %s", result)

            return result

        except Exception:
            logger.exception("Erro ao buscar reservas por data")
            raise

    def has_reservation_on_date(
        self, account_id: str, target_date: date
    ) -> bool:
        """
        Verifica se uma conta já possui reserva em uma data específica.

        Args:
            account_id (str): ID da conta.
            target_date (date): Data alvo.

        Returns:
            bool: True se já houver reserva, False caso contrário.
        """
        try:
            logger.debug(
                "Verificando reserva da conta %s na data %s",
                account_id,
                target_date,
            )

            result = any(
                r.get("account_id") == account_id
                and r.get("date") == target_date.isoformat()
                and r.get("status") == "confirmed"
                for r in self.get_reservations()
            )

            logger.debug("Resultado verificação: %s", result)

            return result

        except Exception:
            logger.exception("Erro ao verificar reserva por data")
            raise

    def get_reserved_account_ids_by_date(
        self, target_date: date
    ) -> List[str]:
        """
        Retorna os IDs das contas que já possuem reserva na data.

        Args:
            target_date (date): Data alvo.

        Returns:
            List[str]: Lista de IDs de contas.
        """
        try:
            logger.debug(
                "Obtendo contas reservadas para a data %s", target_date
            )

            ids = [
                r["account_id"]
                for r in self.get_reservations_by_date(target_date)
            ]

            logger.debug("Contas com reserva: %s", ids)

            return ids

        except Exception:
            logger.exception("Erro ao buscar contas reservadas")
            raise

    def has_future_reservation(
        self, account_id: str, reference_date: date
    ) -> bool:
        """
        Método legado.

        Verifica se existe qualquer reserva futura para a conta.

        NÃO utilizar na lógica nova baseada em data específica.
        """
        try:
            logger.debug(
                "Verificando reserva futura para conta %s", account_id
            )

            for reservation in self.get_reservations():
                if reservation.get("account_id") != account_id:
                    continue

                if reservation.get("status") != "confirmed":
                    continue

                date_str = reservation.get("date")
                if not date_str:
                    continue

                reservation_date = date.fromisoformat(date_str)

                if reservation_date >= reference_date:
                    logger.debug(
                        "Reserva futura encontrada: %s", reservation
                    )
                    return True

            return False

        except Exception:
            logger.exception("Erro ao verificar reserva futura")
            raise

    def add_reservation(
        self,
        account_id: str,
        reservation_date: date,
        hour: str,
        status: str = "confirmed",
    ) -> None:
        """
        Adiciona uma nova reserva ao estado e persiste no arquivo.

        Args:
            account_id (str): ID da conta.
            reservation_date (date): Data da reserva.
            hour (str): Horário da reserva.
            status (str): Status da reserva.
        """
        try:
            logger.debug(
                "Adicionando reserva: conta=%s, data=%s, hora=%s",
                account_id,
                reservation_date,
                hour,
            )

            record = {
                "account_id": account_id,
                "date": reservation_date.isoformat(),
                "hour": hour,
                "status": status,
            }

            self.state["reservations"].append(record)

            self.save()

            logger.info(
                "Reserva registrada → conta=%s | %s %s",
                account_id,
                reservation_date,
                hour,
            )

        except Exception:
            logger.exception("Erro ao adicionar reserva")
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
            logger.debug(
                "Buscando reserva da conta %s (data=%s)",
                account_id,
                reservation_date,
            )

            for reservation in self.get_reservations():
                if reservation.get("account_id") != account_id:
                    continue

                if reservation_date:
                    if reservation.get("date") != reservation_date.isoformat():
                        continue

                logger.debug("Reserva encontrada: %s", reservation)
                return reservation

            logger.debug("Nenhuma reserva encontrada para conta %s", account_id)
            return None

        except Exception:
            logger.exception("Erro ao buscar reserva da conta")
            raise