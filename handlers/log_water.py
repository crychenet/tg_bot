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
