from aiogram import types, Router
from aiogram.filters import Command
import datetime
import os
from config import *
from utils import *
from utils import StorageManager

check_progress_router = Router()


@check_progress_router.message(Command("check_progress"))
async def check_progress(message: types.Message):
    user_id = message.from_user.id
    file_path = os.path.join(PATH_TO_BASE_USERS_INFO, f"{user_id}.json")

    if not await file_exists_async(PATH_TO_BASE_USERS_INFO, f"{user_id}.json"):
        await message.answer("Сначала настройте профиль с помощью /set_profile.")
        return

    user_data = await StorageManager.load_json(file_path)
    date_now = str(datetime.date.today())

    water_norm = user_data.get("water_norm_training", 0) if user_data.get("days_week_of_activity", 0) > 0 else user_data.get("water_norm_rest", 0)
    calorie_norm = user_data.get("calorie_norm", 0)

    water_logged = user_data.get("water_logged", {}).get(date_now, 0)
    calories_logged = user_data.get("calories_logged", {}).get(date_now, 0)
    calories_burned = user_data.get("calories_burned", {}).get(date_now, 0)

    water_remaining = max(water_norm - water_logged, 0)
    calorie_balance = max(calories_logged - calories_burned, 0)

    progress_message = (
        "📊 *Прогресс:*\n"
        "*Вода:*\n"
        f"- Выпито: {water_logged:.2f} мл из {water_norm:.2f} мл.\n"
        f"- Осталось: {water_remaining:.2f} мл.\n\n"
        "*Калории:*\n"
        f"- Потреблено: {calories_logged:.2f} ккал из {calorie_norm:.2f} ккал.\n"
        f"- Сожжено: {calories_burned:.2f} ккал.\n"
        f"- Баланс: {calorie_balance:.2f} ккал."
    )

    await message.answer(progress_message, parse_mode="Markdown")
