from dotenv import load_dotenv
import os
from yandex_cloud_ml_sdk import AsyncYCloudML
import asyncio


load_dotenv()
_model_lock = asyncio.Lock()

YANDEX_SDK_MODEL = None


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


async def start_yandex_model(temperature: float = 0.5, max_tokens: int = 20):
    global YANDEX_SDK_MODEL
    async with _model_lock:
        if YANDEX_SDK_MODEL is None:
            sdk = AsyncYCloudML(folder_id=YANDEX_FOLDER_ID)
            YANDEX_SDK_MODEL = sdk.models.completions("yandexgpt").configure(
                temperature=temperature, max_tokens=max_tokens
            )
    return YANDEX_SDK_MODEL

