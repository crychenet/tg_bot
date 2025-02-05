from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
import datetime
from config import *
from utils import *

log_food_router = Router()


class FoodLoggingState(StatesGroup):
    waiting_for_food_name = State()
    waiting_for_food_amount = State()


@log_food_router.message(Command("log_food"))
async def log_food_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    file_path = PATH_TO_BASE_USERS_INFO / f"{user_id}.json"
    if await file_exists_async(file_path):
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
    food_calories = yandex_gpt_sdk
    date_now = str(datetime.date.today())

    file_path = os.path.join(PATH_TO_BASE_USERS_INFO, f"{message.from_user.id}.json")
    user_data = await StorageManager.load_json(file_path)
    user_data['calories_logged'][date_now] +=
    await StorageManager.save_json(file_path, user_data)







