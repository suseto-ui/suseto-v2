# services/config.py
# Základní konfigurace backendu.

import os
from typing import Any


class Config:
    """Konfigurace aplikace.

    Hodnoty se čtou z environmentu s rozumnými defaulty.
    """

    @property
    def env(self) -> str:
        return os.getenv("SUSETO_ENV", "development")

    @property
    def debug(self) -> bool:
        return os.getenv("SUSETO_DEBUG", "true").lower() == "true"

    @property
    def database_url(self) -> str:
        return os.getenv("SUSETO_DATABASE_URL", "sqlite:///:memory:")

    @property
    def secret_key(self) -> str:
        return os.getenv("SUSETO_SECRET_KEY", "change-me-in-production")

    @property
    def api_prefix(self) -> str:
        return os.getenv("SUSETO_API_PREFIX", "/api")

    def get(self, key: str, default: Any = None) -> Any:
        """Obecné získání hodnoty z envu."""
        return os.getenv(key, default)


# Globální instance pro snadné použití
config = Config()
