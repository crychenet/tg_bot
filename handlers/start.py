from aiogram.filters import Command
from aiogram import types, Router


start_router = Router()


@start_router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.reply(
        "Добро пожаловать! Этот бот предназначен для расчёта нормы воды, калорий и трекинга активности."
    )
