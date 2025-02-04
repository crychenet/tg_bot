from dotenv import load_dotenv
import os

load_dotenv()

YANDEX_FOLDER_ID = os.getenv('YANDEX_FOLDER_ID')
TG_BOT_TOKEN = os.getenv('BOT_TOKEN')
PATH_TO_SYSTEM_PROMPT = os.getenv('PATH_TO_SYSTEM_PROMPT')
PATH_TO_BASE_USERS_INFO = os.getenv('PATH_TO_BASE_USERS_INFO')
OPEN_WEATHER_API_KEY = os.getenv('OPEN_WEATHER_API_KEY')


required_vars = {
    "YANDEX_FOLDER_ID": YANDEX_FOLDER_ID,
    "TG_BOT_TOKEN": TG_BOT_TOKEN,
    "PATH_TO_SYSTEM_PROMPT": PATH_TO_SYSTEM_PROMPT,
    "PATH_TO_BASE_USERS_INFO": PATH_TO_BASE_USERS_INFO,
    'OPEN_WEATHER_API_KEY': OPEN_WEATHER_API_KEY
}

missing_vars = [key for key, value in required_vars.items() if not value]

if missing_vars:
    raise ValueError(f"Не заданы переменные окружения: {', '.join(missing_vars)}.")

