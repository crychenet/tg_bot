from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command


router = Router()


@router.message(Command('start'))
async def cmd_start(message: Message):
    await message.reply(f'Hello!\n/help for list commands')


@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.reply(
        f"You can use:\n"
        f"/start - start"
        f"/form - example dialog"
        f"/keyboard - example button"
        f"/joke - get a random joke"
    )


@router.message(Command('keyboard'))
async def show_keyboard(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Кнопка 1', callback_data='btn1')],
            [InlineKeyboardButton(text='Кнопка 2', callback_data='btn2')],
        ]
    )
    await message.reply('Выберите:', reply_markup=keyboard)
