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
# --- COMPATIBILITY WRAPPER FOR app.py ---
# Tento wrapper umožňuje app.py číst vlastnosti instance `config` jako slovník.
class ConfigWrapper:
    def __init__(self, cfg):
        self._cfg = cfg

    def __getitem__(self, key):
        # Mapování očekávaných velkých klíčů na malé atributy instance
        key_map = {
            "SECRET_KEY": "secret_key",
            "DATABASE_URI": "database_url",
            "ADMIN_USERNAME": "admin_username",
            "DEFAULT_ADMIN_PASSWORD": "default_admin_password"
        }
        attr_name = key_map.get(key, key.lower())
        return getattr(self._cfg, attr_name, None)

    def get(self, key, default=None):
        val = self.__getitem__(key)
        return val if val is not None else default

CONFIG = ConfigWrapper(config)
