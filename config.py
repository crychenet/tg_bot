from dotenv import load_dotenv
import os

load_dotenv()

YANDEX_FOLDER_ID = os.getenv('YANDEX_FOLDER_ID')
TG_BOT_TOKEN = os.getenv('BOT_TOKEN')

if not TG_BOT_TOKEN:
    raise ValueError("Please set BOT_TOKEN environment variable")
