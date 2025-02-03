import asyncio
import os
import json

from aiogram.types import Message
from config import TG_BOT_TOKEN
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

from yandex_gpt_sdk import *
from handlers.profile import profile_router


bot = Bot(token=TG_BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.include_routers(profile_router)


class StorageManager:
    @staticmethod
    async def save_json(file_path, data):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.reply("Добро пожаловать! Я ваш бот.")


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.reply("Я могу ответить на команды /start, /help, /set_profile.")


async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
