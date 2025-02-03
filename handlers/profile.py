from aiogram import types, Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from config import *
from utils import *

profile_router = Router()


class ProfileSetup(StatesGroup):
    weight = State()
    height = State()
    age = State()
    days_week_of_activity = State()
    average_training_time = State()
    city = State()


async def ask_question(message: types.Message, state: FSMContext, question: str, next_state: State):
    await message.answer(question)
    await state.set_state(next_state)


@profile_router.message(Command("set_profile"))
async def cmd_set_profile(message: types.Message, state: FSMContext):
    await ask_question(message, state, "Введите ваш вес (в кг):", ProfileSetup.weight)


@profile_router.message(ProfileSetup.weight)
async def process_weight(message: types.Message, state: FSMContext):
    try:
        valid_message = convert_to_valid_digit(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите число больше 0")
        return

    await state.update_data(weight=valid_message)
    await ask_question(message, state, "Введите ваш рост (в см):", ProfileSetup.height)


@profile_router.message(ProfileSetup.height)
async def process_height(message: types.Message, state: FSMContext):
    try:
        valid_message = convert_to_valid_digit(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите число больше 0")
        return

    await state.update_data(height=valid_message)
    await ask_question(message, state, "Введите ваш возраст:", ProfileSetup.age)


@profile_router.message(ProfileSetup.age)
async def process_age(message: types.Message, state: FSMContext):
    try:
        valid_message = convert_to_valid_digit(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите число больше 0")
        return

    await state.update_data(age=valid_message)
    await ask_question(message, state, "Сколько дней в неделю вы тренируетесь?", ProfileSetup.days_week_of_activity)


@profile_router.message(ProfileSetup.days_week_of_activity)
async def process_days_week_of_activity(message: types.Message, state: FSMContext):
    try:
        valid_message = convert_to_valid_digit(message.text)
        if not (0 <= valid_message <= 7):
            raise ValueError("Должно быть число от 0 до 7")
    except ValueError:
        await message.answer("Введите число от 0 до 7")
        return

    await state.update_data(days_week_of_activity=int(valid_message))
    await ask_question(message, state, "Сколько минут длится ваша средняя тренировка?",
                       ProfileSetup.average_training_time)


@profile_router.message(ProfileSetup.average_training_time)
async def process_average_training_time(message: types.Message, state: FSMContext):
    try:
        valid_message = convert_to_valid_digit(message.text)
    except ValueError:
        await message.answer("Введите число больше 0")
        return

    await state.update_data(average_training_time=int(valid_message))
    await ask_question(message, state, "В каком городе вы находитесь?", ProfileSetup.city)


@profile_router.message(ProfileSetup.city)
async def process_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)

    user_data = await state.get_data()
    file_path = os.path.join(PATH_TO_BASE_USERS_INFO, str(message.from_user.id) + '.json')
    await StorageManager.save_json(file_path, user_data)

    response = (f"✅ Ваш профиль:\n"
                f"📌 Вес: {user_data['weight']} кг\n"
                f"📏 Рост: {user_data['height']} см\n"
                f"🎂 Возраст: {user_data['age']} лет\n"
                f"🏃‍♂️ Дни активности в неделю: {user_data['days_week_of_activity']}\n"
                f"⏳ Среднее время тренировки: {user_data['average_training_time']} мин\n"
                f"🌍 Город: {user_data['city']}")

    await message.answer(response)
    await state.clear()
