import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def get_config():
    return {
        "SECRET_KEY": os.getenv("SUSETO_SECRET_KEY", "dev-secret-change-me"),
        "DATA_DIR": DATA_DIR,
        "ADMIN_USERNAME": os.getenv("SUSETO_ADMIN_USERNAME", "admin"),
        "DEFAULT_ADMIN_PASSWORD": os.getenv("SUSETO_ADMIN_PASSWORD", "Admin123!"),
    }


CONFIG = get_config()
