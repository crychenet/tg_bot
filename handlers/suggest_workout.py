from aiogram import types, Router
from aiogram.filters import Command
import datetime
import json

from config import *
from utils import *
from yandex_gpt_sdk import simple_request

suggest_workout_router = Router()


@suggest_workout_router.message(Command("suggest_workout"))
async def suggest_workout(message: types.Message):
    user_id = message.from_user.id

    if not await file_exists_async(PATH_TO_BASE_USERS_INFO, f"{user_id}.json"):
        await message.answer("Сначала настройте профиль с помощью /set_profile.")
        return

    workout_suggestion = await simple_request(
        message='Напиши тренировку',
        type_message='suggest_workout',
        user_id=user_id
    )

    suggested_workout = workout_suggestion.alternatives[0].text

    await message.answer(f"💪 *Рекомендованная тренировка:*\n\n{suggested_workout}", parse_mode="Markdown")
