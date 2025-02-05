from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State

from config import *
from utils import *
from yandex_gpt_sdk import simple_request

suggest_meal_router = Router()


class MealSuggestionState(StatesGroup):
    waiting_for_goal = State()


@suggest_meal_router.message(Command("suggest_meal"))
async def suggest_meal_start(message: types.Message, state: FSMContext):
    await ask_question(message, state, "Вы хотите похудеть или набрать вес? Напишите ваш выбор.",
                       MealSuggestionState.waiting_for_goal)


@suggest_meal_router.message(MealSuggestionState.waiting_for_goal)
async def suggest_meal_goal(message: types.Message, state: FSMContext):
    goal = message.text.lower().strip()

    if goal not in ["похудеть", "набрать"]:
        await message.answer("Пожалуйста, выберите: похудеть или набрать.")
        return

    user_id = message.from_user.id

    if not await file_exists_async(PATH_TO_BASE_USERS_INFO, f"{user_id}.json"):
        await message.answer("Сначала настройте профиль с помощью /set_profile.")
        return

    meal_suggestion = await simple_request(
        message=f"Напиши {goal} план питания",
        type_message="suggest_meal",
        user_id=user_id
    )

    suggested_meal = meal_suggestion.alternatives[0].text

    await message.answer(f"🍽 *Рекомендованное питание ({goal}):*\n\n{suggested_meal}", parse_mode="Markdown")

    await state.clear()
