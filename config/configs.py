import os
from dotenv import load_dotenv
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

load_dotenv()
filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

BOT_TOKEN = os.getenv("BOT_TOKEN")