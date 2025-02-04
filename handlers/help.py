from aiogram.filters import Command
from aiogram import types, Router


help_router = Router()


@help_router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.reply("Я могу ответить на команды /start, /help, /set_profile.")
