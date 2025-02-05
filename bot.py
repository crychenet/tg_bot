import asyncio
import os
import json

from config import TG_BOT_TOKEN
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import logging

from yandex_gpt_sdk import *
from handlers.profile import profile_router
from handlers.start import start_router
from handlers.help import help_router
from handlers.log_water import log_water_router
from handlers.log_food import log_food_router
from handlers.log_workout import log_workout_router
from handlers.check_progress import check_progress_router
from handlers.suggest_workout import suggest_workout_router
from handlers.suggest_meal import suggest_meal_router
from handlers.check_progress_graph import check_progress_graphs_router
from middlewares.logging_middleware import LoggingMiddleware

from utils import update_daily_weather_consumption, set_up_user_calories_and_water_data


bot = Bot(token=TG_BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.include_routers(profile_router, start_router, help_router,
                   log_water_router, log_food_router, log_workout_router,
                   check_progress_router, suggest_workout_router,
                   suggest_meal_router, check_progress_graphs_router)
dp.message.middleware(LoggingMiddleware())
dp.callback_query.middleware(LoggingMiddleware())


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%b %d %I:%M:%S %p",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logging.getLogger("aiogram").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def main():
    print("Бот запущен!")
    bot_task = asyncio.create_task(dp.start_polling(bot))
    update_daily_weather_consumption_task = asyncio.create_task(update_daily_weather_consumption(600))
    set_up_user_calories_and_water_data_task = asyncio.create_task(set_up_user_calories_and_water_data(10000))

    await asyncio.gather(
        bot_task, update_daily_weather_consumption_task,
        set_up_user_calories_and_water_data_task
    )


if __name__ == "__main__":
    asyncio.run(main())
