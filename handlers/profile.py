import datetime

from aiogram import types, Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from config import *
from utils import *
from open_weather_api import download_weather_data

profile_router = Router()


class ProfileSetup(StatesGroup):
    sex = State()
    weight = State()
    height = State()
    age = State()
    days_week_of_activity = State()
    average_training_time = State()
    city = State()
    water_goal = State()
    calorie_goal = State()


async def ask_question(message: types.Message, state: FSMContext, question: str, next_state: State):
    await message.answer(question)
    await state.set_state(next_state)


@profile_router.message(Command("set_profile"))
async def cmd_set_profile(message: types.Message, state: FSMContext):
    await ask_question(message, state, "Введите ваш пол (М/Ж):", ProfileSetup.sex)


@profile_router.message(ProfileSetup.sex)
async def process_sex(message: types.Message, state: FSMContext):
    valid_sex = message.text.strip().lower()

    if valid_sex not in ["м", "ж"]:
        await message.answer("Пожалуйста, введите 'М' (мужской) или 'Ж' (женский).")
        return

    await state.update_data(sex=valid_sex.upper())
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
    user_data = await state.get_data()
    user_data["city"] = message.text.strip()

    weight = user_data["weight"]
    height = user_data["height"]
    age = user_data["age"]
    average_training_time = user_data["average_training_time"]

    try:
        weather_data = await download_weather_data(user_data["city"], OPEN_WEATHER_API_KEY)
        air_temperature = weather_data[user_data["city"]]
    except Exception as e:
        air_temperature = 22
        await message.answer(f"Не удалось получить данные о погоде. Устанавливаем температуру {air_temperature}°C.")

    water_norm_training = calculate_water_consumption_rate(weight, average_training_time, air_temperature,
                                                           training_day=True)
    water_norm_rest = calculate_water_consumption_rate(weight, average_training_time, air_temperature,
                                                       training_day=False)

    calorie_norm = calculate_calorie_intake_rate(weight, height, age)
    date_now = str(datetime.date.today())

    user_data["water_norm_training"] = water_norm_training
    user_data["water_norm_rest"] = water_norm_rest
    user_data["calorie_norm"] = calorie_norm
    user_data["air_temperature"] = air_temperature
    user_data['water_logged'] = {date_now: 0}
    user_data['calories_logged'] = {date_now: 0}
    user_data['calories_burned'] = {date_now: 0}

    file_path = os.path.join(PATH_TO_BASE_USERS_INFO, f"{message.from_user.id}.json")
    await StorageManager.save_json(file_path, user_data)

    response = (f"✅ Ваш профиль:\n"
                f"⚧ Пол: {user_data['sex']}\n"
                f"📌 Вес: {user_data['weight']} кг\n"
                f"📏 Рост: {user_data['height']} см\n"
                f"🎂 Возраст: {user_data['age']} лет\n"
                f"🏃‍♂️ Дни активности в неделю: {user_data['days_week_of_activity']}\n"
                f"⏳ Среднее время тренировки: {user_data['average_training_time']} мин\n"
                f"🌍 Город: {user_data['city']} (Температура: {air_temperature}°C)\n"
                f"\n🚰 Норма воды:\n"
                f"   💧 В тренировочный день: {water_norm_training:.2f} мл\n"
                f"   💧 В обычный день: {water_norm_rest:.2f} мл\n"
                f"\n🔥 Норма калорий: {calorie_norm:.2f} ккал")

    await message.answer(response)
    await state.clear()
