import asyncio
import os
import datetime
from config import *
import aiofiles
from typing import Dict, Any, Optional
import json
from open_weather_api import download_weather_data


class StorageManager:
    @staticmethod
    async def load_json(file_path: str) -> Dict[str, Any]:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            return json.loads(content)

    @staticmethod
    async def save_json(file_path: str, data: Dict[str, Any]):
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            json_data = json.dumps(data, indent=4, ensure_ascii=False)
            await f.write(json_data)


def convert_to_valid_digit(value: str) -> float:
    value = value.strip().replace(',', '.')
    try:
        number = float(value)
        if number >= 0:
            return number
        else:
            raise ValueError("Число должно быть больше 0")
    except ValueError:
        raise ValueError("Неверный формат числа")


def calculate_water_consumption_rate(
        weight: float, average_training_time: float, air_temperature: float, training_day: bool = True
):
    """average_training_time in minutes"""
    if training_day:
        average_training_time_in_minutes = average_training_time / 30
        if air_temperature <= 25:
            return 30 * weight + 500 * average_training_time_in_minutes
        elif air_temperature <= 30:
            return 30 * weight + 750 * average_training_time_in_minutes
        else:
            return 30 * weight + 1000 * average_training_time_in_minutes
    else:
        return 30 * weight


def calculate_calorie_intake_rate(weight: float, height: float, age: int):
    return 10 * weight + 6.25 * height - 5 * age


async def update_daily_weather_consumption(delay):
    """delay in minutes"""
    while True:
        for path_to_file in os.listdir(PATH_TO_BASE_USERS_INFO):
            user_data = await StorageManager.load_json(os.path.join(PATH_TO_BASE_USERS_INFO, path_to_file))
            air_temperature = await download_weather_data(user_data['city'], OPEN_WEATHER_API_KEY)

            user_data['water_norm_training'] = calculate_water_consumption_rate(
                user_data['weight'], user_data['average_training_time'], air_temperature, training_day=True
            )
            user_data['water_norm_rest'] = calculate_water_consumption_rate(
                user_data['weight'], user_data['average_training_time'], air_temperature, training_day=False
            )

            user_data['calorie_norm'] = calculate_calorie_intake_rate(
                user_data['weight'], user_data['height'], user_data['age']
            )
            await StorageManager.save_json(file_path=os.path.join(PATH_TO_BASE_USERS_INFO, path_to_file), data=user_data)
        await asyncio.sleep(60 * delay)


async def set_up_user_calories_and_water_data(delay: int = 86400) -> None:
    """delay in seconds"""
    while True:
        await asyncio.sleep(delay)
        date_now = str(datetime.datetime.now().date())
        for path_to_file in os.listdir(PATH_TO_BASE_USERS_INFO):
            user_data = await StorageManager.load_json(os.path.join(PATH_TO_BASE_USERS_INFO, path_to_file))
            user_data['calories_logged'][date_now] = 0
            user_data['water_logged'][date_now] = 0
            user_data['calories_burned'][date_now] = 0
            await StorageManager.save_json(file_path=os.path.join(PATH_TO_BASE_USERS_INFO, path_to_file),
                                           data=user_data)
