import os
import json
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """
    Classe responsável por carregar e armazenar todas as configurações
    do sistema a partir de variáveis de ambiente.
    """

    def __init__(self) -> None:
        logger.info("Inicializando configuração do sistema")
        self.accounts: List[Dict[str, Any]] = self._load_accounts()
        self.min_window_size: int = self._get_int_env("MIN_WINDOW_SIZE")
        self.max_window_size: int = self._get_int_env("MAX_WINDOW_SIZE")
        self.lookahead_weeks: int = self._get_int_env("LOOKAHEAD_WEEKS")
        self.target_hours: List[str] = self._get_json_env("TARGET_HOURS_JSON")
        self.activity_name: str = self._get_env("ACTIVITY_NAME")
        self.regional_name: str = self._get_env("REGIONAL_NAME")
        self.unit_name: str = self._get_env("UNIT_NAME")
        self.capacity: int = self._get_int_env("CAPACITY")
        self.smtp_host: str = self._get_env("SMTP_SERVER")
        self.smtp_port: int = self._get_int_env("SMTP_PORT")
        self.smtp_user: str = self._get_env("SMTP_USER")
        self.smtp_pass: str = self._get_env("SMTP_PASS")
        self.notify_to: str = self._get_env("NOTIFY_TO")
        self.accepted_windows: List[List[str]] = self._get_json_env("ACCEPTED_WINDOWS_JSON")
        
        self.url: str = self._get_env("URL")
        
        # Evolution API Configs
        self.evolution_url: str = self._get_env("EVOLUTION_API_URL")
        self.evolution_instance: str = self._get_env("EVOLUTION_API_INSTANCE")
        self.evolution_key: str = self._get_env("EVOLUTION_API_KEY")
        self.whatsapp_group_jid: str = self._get_env("WHATSAPP_GROUP_JID")

        logger.debug("Configuração carregada com sucesso")

    def _get_env(self, name: str, required: bool = True) -> str:
        """
        Obtém variável de ambiente.

        Args:
            name (str): Nome da variável.
            required (bool): Se é obrigatória.

        Returns:
            str: Valor da variável.
        """
        value = os.getenv(name)

        if required and not value:
            logger.error(f"Variável obrigatória não encontrada: {name}")
            raise ValueError(f"Missing environment variable: {name}")

        return value or ""

    def _get_int_env(self, name: str, default: Optional[int] = None) -> int:
        """
        Obtém variável de ambiente como inteiro.
        """
        value = os.getenv(name)

        if value is None:
            if default is not None:
                return default

            logger.error(f"Variável obrigatória não encontrada: {name}")
            raise ValueError(f"Missing environment variable: {name}")

        try:
            return int(value)
        except ValueError:
            logger.exception(f"Erro ao converter {name} para inteiro")
            raise

    def _get_json_env(self, name: str) -> Any:
        """
        Obtém variável JSON do ambiente.
        """
        value = self._get_env(name)

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            logger.exception(f"Erro ao fazer parse do JSON: {name}")
            raise

    def _load_accounts(self) -> List[Dict[str, Any]]:
        """
        Carrega contas do secret do GitHub.

        Returns:
            List[Dict]: Lista de contas válidas.
        """
        logger.info("Carregando contas do ambiente")

        accounts = self._get_json_env("RESERVA_ACCOUNTS_JSON")

        if not isinstance(accounts, list):
            logger.error("Formato inválido para RESERVA_ACCOUNTS_JSON")
            raise ValueError("RESERVA_ACCOUNTS_JSON deve ser uma lista")

        for acc in accounts:
            if "login" not in acc or "password" not in acc:
                logger.error(f"Conta inválida encontrada: {acc}")
                raise ValueError("Conta inválida: login e password obrigatórios")

        logger.info(f"{len(accounts)} contas carregadas com sucesso")
        return accounts