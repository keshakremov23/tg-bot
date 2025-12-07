# config.py
import os 
from urllib.parse import urlparse
from dotaenv import load_dotaenv

load_dotaenv()

TOKEN = os.getenv("BOT_TOKEN")
PROXY_TOKEN = os.getenv("PROXY_URL")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin@127.0.0.1:5432/tg-bot")

def parse_db_url(db_url):
    parsed = urlparse(db_url)
    
    return {
        'dbname': parsed.path[1:],
        'user': parsed.username,
        'password': parsed.password,
        'host': parsed.hostname,
        'port': parsed.port
    }

DB_CONFIG = parse_db_url(DATABASE_URL)