import asyncio
import os
import json

from config import TG_BOT_TOKEN
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from yandex_gpt_sdk import *
from handlers.profile import profile_router
from handlers.start import start_router
from handlers.help import help_router
from handlers.loger_information import log_router

from utils import update_daily_weather_consumption, set_up_user_calories_and_water_data


bot = Bot(token=TG_BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.include_routers(profile_router, start_router, help_router, log_router)


async def main():
    print("Бот запущен!")
    bot_task = asyncio.create_task(dp.start_polling(bot))
    update_daily_weather_consumption_task = asyncio.create_task(update_daily_weather_consumption(60))
    set_up_user_calories_and_water_data_task = asyncio.create_task(set_up_user_calories_and_water_data(60))
    yandex_gpt_session_cleaner_task = asyncio.create_task(start_session_cleaner(600))

    await asyncio.gather(
        bot_task, update_daily_weather_consumption_task,
        set_up_user_calories_and_water_data_task, yandex_gpt_session_cleaner_task
    )


if __name__ == "__main__":
    asyncio.run(main())
