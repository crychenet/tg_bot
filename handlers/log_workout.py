from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
import datetime
import json
import os

from config import *
from utils import *
from yandex_gpt_sdk import simple_request

log_workout_router = Router()


class WorkoutLoggingState(StatesGroup):
    waiting_for_workout_name = State()
    waiting_for_workout_duration = State()


@log_workout_router.message(Command("log_workout"))
async def log_workout_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if not await file_exists_async(PATH_TO_BASE_USERS_INFO, f"{user_id}.json"):
        await message.answer("Сначала настройте профиль с помощью /set_profile.")
        return
    await ask_question(message, state, "Введите название тренировки:", WorkoutLoggingState.waiting_for_workout_name)


@log_workout_router.message(WorkoutLoggingState.waiting_for_workout_name)
async def log_workout_name(message: types.Message, state: FSMContext):
    await state.update_data(waiting_for_workout_name=message.text)
    await ask_question(
        message, state,
        "Сколько минут длилась тренировка (введите число):", WorkoutLoggingState.waiting_for_workout_duration)


@log_workout_router.message(WorkoutLoggingState.waiting_for_workout_duration)
async def log_workout_duration(message: types.Message, state: FSMContext):
    try:
        valid_message = convert_to_valid_digit(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите число больше 0")
        return
    await state.update_data(waiting_for_workout_duration=valid_message)

    workout_user_data = await state.get_data()
    print(f'{workout_user_data=}')
    calories_burned = await simple_request(
        message=json.dumps(workout_user_data, ensure_ascii=False),
        type_message='calorie_burn',
        user_id=message.from_user.id
    )
    print(f"{calories_burned.alternatives[0].text=}")
    valid_calories_burned = convert_to_valid_digit(calories_burned.alternatives[0].text)

    date_now = str(datetime.date.today())

    file_path = os.path.join(PATH_TO_BASE_USERS_INFO, f"{message.from_user.id}.json")
    user_data = await StorageManager.load_json(file_path)
    user_data['calories_burned'][date_now] += valid_calories_burned
    await StorageManager.save_json(file_path, user_data)
    await message.answer(
        f"✅ Записано {valid_calories_burned} сожженных калорий\n"
        f"Дополнительно: выпейте {float(workout_user_data['waiting_for_workout_duration']) / 30 * 200:.2f} мл воды.")

    await state.clear()
