import asyncio
from aiogram.types import Message
from config import TG_BOT_TOKEN
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from yandex_gpt_sdk import *


bot = Bot(token=TG_BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.reply("Добро пожаловать! Я ваш бот.")


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.reply("Я могу ответить на команды /start, /help, /set_profile.")


class ProfileSetup(StatesGroup):
    weight = State()
    height = State()
    age = State()
    activity = State()
    city = State()


async def ask_question(message: types.Message, state: FSMContext, question: str, next_state: State):
    await message.answer(question)
    await state.set_state(next_state)


def convert_to_valid_digit(value: str) -> float:
    value = value.strip().replace(',', '.')
    try:
        number = float(value)
        if number > 0:
            return number
        else:
            raise ValueError("Число должно быть больше 0")
    except ValueError:
        raise ValueError("Неверный формат числа")


@dp.message(Command("set_profile"))
async def cmd_set_profile(message: types.Message, state: FSMContext):
    await ask_question(message, state, "Введите ваш вес (в кг):", ProfileSetup.weight)


@dp.message(ProfileSetup.weight)
async def process_weight(message: types.Message, state: FSMContext):
    try:
        valid_message = convert_to_valid_digit(message.text)
    except ValueError:
        await message.answer("❌ Пожалуйста, введите число больше 0")
        return

    await state.update_data(weight=float(valid_message))
    await ask_question(message, state, "Введите ваш рост (в см):", ProfileSetup.height)


@dp.message(ProfileSetup.height)
async def process_height(message: types.Message, state: FSMContext):
    try:
        valid_message = convert_to_valid_digit(message.text)
    except ValueError:
        await message.answer("❌ Пожалуйста, введите число больше 0")
        return

    await state.update_data(height=float(valid_message))
    await ask_question(message, state, "Введите ваш возраст:", ProfileSetup.age)


@dp.message(ProfileSetup.age)
async def process_age(message: types.Message, state: FSMContext):
    try:
        valid_message = convert_to_valid_digit(message.text)
    except ValueError:
        await message.answer("❌ Пожалуйста, введите число больше 0")
        return

    await state.update_data(age=float(valid_message))
    await ask_question(message, state, "Сколько минут активности у вас в день?", ProfileSetup.activity)


@dp.message(ProfileSetup.activity)
async def process_activity(message: types.Message, state: FSMContext):
    await state.update_data(activity=message.text)
    await ask_question(message, state, "В каком городе вы находитесь?", ProfileSetup.city)


@dp.message(ProfileSetup.city)
async def process_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)

    user_data = await state.get_data()
    file_path = os.path.join(PATH_TO_BASE_USERS_INFO, str(message.from_user.id) + '.json')
    await StorageManager.save_json(
        file_path=file_path,
        data=user_data
    )
    response = (f"✅ Ваш профиль:\n"
                f"📌 Вес: {user_data['weight']} кг\n"
                f"📏 Рост: {user_data['height']} см\n"
                f"🎂 Возраст: {user_data['age']}\n"
                f"🏃‍♂️ Активность: {user_data['activity']} мин/день\n"
                f"🌍 Город: {user_data['city']}")

    await message.answer(response)
    await state.clear()


async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


