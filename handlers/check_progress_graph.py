import os
import json
import matplotlib.pyplot as plt
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from aiogram.fsm.context import FSMContext
from config import *
from utils import *


check_progress_graphs_router = Router()


async def load_user_data(user_id):
    file_path = os.path.join(PATH_TO_BASE_USERS_INFO, f"{user_id}.json")
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def plot_progress(user_data, user_id):
    dates = list(user_data["water_logged"].keys())

    plt.figure(figsize=(8, 4))
    plt.plot(dates, user_data["water_logged"].values(), marker="o", linestyle="-", label="Выпито воды (мл)")
    plt.axhline(y=user_data["water_norm_training"], color="r", linestyle="--", label="Норма (тренировочный день)")
    plt.axhline(y=user_data["water_norm_rest"], color="g", linestyle="--", label="Норма (отдых)")
    plt.xlabel("Дата")
    plt.ylabel("Объем (мл)")
    plt.title("Прогресс по потреблению воды")
    plt.legend()
    plt.xticks(rotation=45)
    plt.grid(True)
    water_plot_path = f"water_progress_{user_id}.png"
    plt.savefig(water_plot_path)
    plt.close()

    calorie_balance = [
        user_data["calories_logged"][date] - user_data["calories_burned"][date]
        for date in dates
    ]

    plt.figure(figsize=(8, 4))
    plt.plot(dates, calorie_balance, marker="o", linestyle="-", label="Баланс калорий")
    plt.axhline(y=user_data["calorie_norm"], color="r", linestyle="--", label="Норма калорий")
    plt.xlabel("Дата")
    plt.ylabel("Калории")
    plt.title("Баланс калорий")
    plt.legend()
    plt.xticks(rotation=45)
    plt.grid(True)
    calories_plot_path = f"calories_balance_{user_id}.png"
    plt.savefig(calories_plot_path)
    plt.close()

    return water_plot_path, calories_plot_path


@check_progress_graphs_router.message(Command("check_progress_graphs"))
async def check_progress(message: types.Message):
    user_data = await load_user_data(message.from_user.id)
    if not user_data:
        await message.answer("Данные не найдены. Пожалуйста, сначала введите свою информацию.")
        return

    water_plot, calories_plot = plot_progress(user_data, message.from_user.id)

    await message.answer_photo(FSInputFile(water_plot), caption="Ваш прогресс по воде")
    await message.answer_photo(FSInputFile(calories_plot), caption="Ваш прогресс по калориям")

    os.remove(water_plot)
    os.remove(calories_plot)
