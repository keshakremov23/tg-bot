import os 
from dotaenv import load_dotaenv

load_dotaenv()

TOKEN = os.getenv("BOT_TOKEN")
PROXY_TOKEN = os.getenv("PROXY_URL")