from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
import datetime
from config import *
from utils import *

log_water_router = Router()


class WaterLoggingState(StatesGroup):
    waiting_for_water_amount = State()


@log_water_router.message(Command("log_water"))
async def log_water_start(message: types.Message, state: FSMContext):
    await message.answer("Введите количество выпитой воды (в мл):")
    await state.set_state(WaterLoggingState.waiting_for_water_amount)


@log_water_router.message(WaterLoggingState.waiting_for_water_amount)
async def log_water_intake(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    file_path = os.path.join(PATH_TO_BASE_USERS_INFO, f"{user_id}.json")

    try:
        valid_message = convert_to_valid_digit(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите число больше 0")
        return

    try:
        user_data = await StorageManager.load_json(file_path)
    except FileNotFoundError:
        await message.answer("Сначала настройте профиль с помощью /set_profile.")
        await state.clear()
        return

    date_now = str(datetime.date.today())
    user_data['water_logged'][date_now] += valid_message
    await StorageManager.save_json(file_path, user_data)

    water_to_norm_during_training = max(0, user_data["water_norm_training"] - user_data["water_logged"][date_now])
    water_to_norm_during_rest = max(0, user_data["water_norm_rest"] - user_data["water_logged"][date_now])

    await message.answer(f"✅ Добавлено {valid_message} мл воды.\n"
                         f"🚰 Осталось до цели:\n"
                         f"  💧 В тренировочный день: {water_to_norm_during_training:.2f} мл\n"
                         f"  💧 В обычный день: {water_to_norm_during_rest:.2f} мл\n")

    await state.clear()


# @log_router.message(Command("log_food"))
# async def log_food_intake(message: types.Message, state: FSMContext):
#     args = message.text.split(maxsplit=1)
#
#     if len(args) < 2:
#         await message.answer("Использование: /log_food <название продукта>")
#         return
#
#     food_name = args[1]
#     food_info = await get_food_info(food_name)
#
#     if not food_info:
#         await message.answer("Не удалось получить данные о продукте.")
#         return
#
#     user_id = message.from_user.id
#     file_path = os.path.join(PATH_TO_BASE_USERS_INFO, f"{user_id}.json")
#     user_data = await StorageManager.load_json(file_path)
#
#     if not user_data:
#         await message.answer("Сначала настройте профиль с помощью /set_profile.")
#         return
#
#     user_data.setdefault("calories_logged", 0)
#     user_data["calories_logged"] += food_info["calories"]
#
#     daily_calorie_goal = user_data.get("calorie_norm", 2000)
#     remaining_calories = max(daily_calorie_goal - user_data["calories_logged"], 0)
#
#     await StorageManager.save_json(file_path, user_data)
#
#     await message.answer(f"✅ Добавлен продукт: {food_info['name']}.\n"
#                          f"🔥 Калорийность: {food_info['calories']} ккал.\n"
#                          f"⚡ Осталось до цели: {remaining_calories:.2f} ккал")
#
#
# @log_router.message(Command("log_workout"))
# async def log_workout(message: types.Message, state: FSMContext):
#     args = message.text.split(maxsplit=2)
#
#     if len(args) < 3 or not args[2].isdigit():
#         await message.answer("Использование: /log_workout <тип тренировки> <время (мин)>")
#         return
#
#     workout_type = args[1]
#     duration = int(args[2])
#
#     user_id = message.from_user.id
#     file_path = os.path.join(PATH_TO_BASE_USERS_INFO, f"{user_id}.json")
#     user_data = await StorageManager.load_json(file_path)
#
#     if not user_data:
#         await message.answer("Сначала настройте профиль с помощью /set_profile.")
#         return
#
#     weight = user_data.get("weight", 70)
#     burned_calories = await calculate_burned_calories(workout_type, duration, weight)
#
#     user_data.setdefault("calories_burned", 0)
#     user_data["calories_burned"] += burned_calories
#
#     await StorageManager.save_json(file_path, user_data)
#
#     await message.answer(f"✅ Записана тренировка: {workout_type}, {duration} мин.\n"
#                          f"🔥 Сожжено калорий: {burned_calories:.2f} ккал")
#
