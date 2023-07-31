import os
from dotenv import load_dotenv
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

load_dotenv()
filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")