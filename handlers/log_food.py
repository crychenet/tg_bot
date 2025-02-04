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
    await message.answer("Введите название съеденной еды:")
    await state.set_state(FoodLoggingState.waiting_for_food_name)


@log_food_router.message(FoodLoggingState.waiting_for_food_name)
async def log_food_intake(message: types.Message, state: FSMContext):



