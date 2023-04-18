from pathlib import Path

CONFIG_PATH = Path(".").parent.parent / "config"
DATA_PATH = Path(".").parent.parent / "data"

CONFIG_JSON = CONFIG_PATH / "config.json"
GOOGLE_CONFIG = CONFIG_PATH / "google_spreadsheet_access.json"
ENV_VARS = CONFIG_PATH / ".env"

DATABASE = DATA_PATH / "stravadictos.db"
DATABASE_TEMPLATE = DATA_PATH / "stravadictos_template.db"
