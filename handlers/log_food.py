from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
import datetime
from pathlib import Path

from config import *
from utils import *
from yandex_gpt_sdk import simple_request

log_food_router = Router()


class FoodLoggingState(StatesGroup):
    waiting_for_food_name = State()
    waiting_for_food_amount = State()


@log_food_router.message(Command("log_food"))
async def log_food_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if not await file_exists_async(PATH_TO_BASE_USERS_INFO, f"{user_id}.json"):
        await message.answer("Сначала настройте профиль с помощью /set_profile.")
        return
    await ask_question(message, state, "Введите название съеденной еды:", FoodLoggingState.waiting_for_food_name)


@log_food_router.message(FoodLoggingState.waiting_for_food_name)
async def log_food_name(message: types.Message, state: FSMContext):
    await state.update_data(waiting_for_food_name=message.text)
    await ask_question(
        message, state,
        "Сколько примерно граммов вы съели (введите число):", FoodLoggingState.waiting_for_food_amount)


@log_food_router.message(FoodLoggingState.waiting_for_food_amount)
async def log_food_amount(message: types.Message, state: FSMContext):
    try:
        valid_message = convert_to_valid_digit(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите число больше 0")
        return
    await state.update_data(waiting_for_food_amount=valid_message)
    food_user_data = await state.get_data()
    print(f'{food_user_data=}')

    food_calories = await simple_request(
        message=json.dumps(food_user_data, ensure_ascii=False),
        type_message='calorie_count',
        user_id=message.from_user.id
    )

    print(f'{food_calories.alternatives[0].text=}')

    valid_food_calories = convert_to_valid_digit(food_calories.alternatives[0].text)

    date_now = str(datetime.date.today())

    file_path = os.path.join(PATH_TO_BASE_USERS_INFO, f"{message.from_user.id}.json")
    user_data = await StorageManager.load_json(file_path)
    user_data['calories_logged'][date_now] += valid_food_calories
    await StorageManager.save_json(file_path, user_data)
    await message.answer(f"✅ Добавлено {valid_food_calories}")

    await state.clear()
