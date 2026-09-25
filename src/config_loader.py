import yaml
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


def load_config(config_path: Path = None) -> dict:
    """Ładuje konfigurację z pliku YAML i zmiennych środowiskowych."""
    if config_path is None:
        config_path = BASE_DIR / "config" / "config.yaml"

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    db = config["database"]
    db["host"] = os.getenv("DB_HOST", db["host"])
    db["port"] = os.getenv("DB_PORT", db["port"])
    db["name"] = os.getenv("DB_NAME", db["name"])
    db["user"] = os.getenv("DB_USER", db["user"])
    db["password"] = os.getenv("DB_PASSWORD", db["password"])

    return config