from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from config import *
from utils import *
import os


log_router = Router()


async def get_food_info(product_name: str):
    return {"name": product_name, "calories": 100}


async def calculate_burned_calories(workout_type: str, duration: int, weight: float):
    return duration * 5


@log_router.message(Command("log_water"))
async def log_water_intake(message: types.Message, state: FSMContext):
    args = message.text.split(maxsplit=1)

    if len(args) < 2 or not args[1].isdigit():
        await message.answer("Использование: /log_water <количество (мл)>")
        return

    water_amount = int(args[1])
    user_id = message.from_user.id

    file_path = os.path.join(PATH_TO_BASE_USERS_INFO, f"{user_id}.json")
    user_data = await StorageManager.load_json(file_path)

    if not user_data:
        await message.answer("Сначала настройте профиль с помощью /set_profile.")
        return

    user_data.setdefault("water_logged", 0)
    user_data["water_logged"] += water_amount

    daily_goal = user_data.get("water_norm_training", 2000)
    remaining = max(daily_goal - user_data["water_logged"], 0)

    await StorageManager.save_json(file_path, user_data)

    await message.answer(f"✅ Добавлено {water_amount} мл воды.\n"
                         f"💧 Осталось до цели: {remaining:.2f} мл")


@log_router.message(Command("log_food"))
async def log_food_intake(message: types.Message, state: FSMContext):
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.answer("Использование: /log_food <название продукта>")
        return

    food_name = args[1]
    food_info = await get_food_info(food_name)

    if not food_info:
        await message.answer("Не удалось получить данные о продукте.")
        return

    user_id = message.from_user.id
    file_path = os.path.join(PATH_TO_BASE_USERS_INFO, f"{user_id}.json")
    user_data = await StorageManager.load_json(file_path)

    if not user_data:
        await message.answer("Сначала настройте профиль с помощью /set_profile.")
        return

    user_data.setdefault("calories_logged", 0)
    user_data["calories_logged"] += food_info["calories"]

    daily_calorie_goal = user_data.get("calorie_norm", 2000)
    remaining_calories = max(daily_calorie_goal - user_data["calories_logged"], 0)

    await StorageManager.save_json(file_path, user_data)

    await message.answer(f"✅ Добавлен продукт: {food_info['name']}.\n"
                         f"🔥 Калорийность: {food_info['calories']} ккал.\n"
                         f"⚡ Осталось до цели: {remaining_calories:.2f} ккал")


@log_router.message(Command("log_workout"))
async def log_workout(message: types.Message, state: FSMContext):
    args = message.text.split(maxsplit=2)

    if len(args) < 3 or not args[2].isdigit():
        await message.answer("Использование: /log_workout <тип тренировки> <время (мин)>")
        return

    workout_type = args[1]
    duration = int(args[2])

    user_id = message.from_user.id
    file_path = os.path.join(PATH_TO_BASE_USERS_INFO, f"{user_id}.json")
    user_data = await StorageManager.load_json(file_path)

    if not user_data:
        await message.answer("Сначала настройте профиль с помощью /set_profile.")
        return

    weight = user_data.get("weight", 70)
    burned_calories = await calculate_burned_calories(workout_type, duration, weight)

    user_data.setdefault("calories_burned", 0)
    user_data["calories_burned"] += burned_calories

    await StorageManager.save_json(file_path, user_data)

    await message.answer(f"✅ Записана тренировка: {workout_type}, {duration} мин.\n"
                         f"🔥 Сожжено калорий: {burned_calories:.2f} ккал")

