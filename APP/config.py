# config.py - простой вариант
import os
from urllib.parse import urlparse

# Прямые значения
TOKEN = "8478765106:AAEjPiQJpgXJ_er-5_U0U-HS6xVGwIbvrxU"
PROXY_URL = "http://P89FcB:T6ot1M@170.246.55.245:9603"
DATABASE_URL = "postgresql://admin:admin@localhost:5432/tg-bot"

def parse_db_url(db_url):
    parsed = urlparse(db_url)
    return {
        'dbname': parsed.path[1:] if parsed.path else 'tg-bot',
        'user': parsed.username or 'admin',
        'password': parsed.password or 'admin',
        'host': parsed.hostname or 'localhost',
        'port': parsed.port or 5432
    }

DB_CONFIG = parse_db_url(DATABASE_URL)

# Для совместимости с admin_panel.py
ADMIN_ID = 1035088857