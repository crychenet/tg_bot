import aiofiles
from typing import Dict, Any
import json


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
        if number > 0:
            return number
        else:
            raise ValueError("Число должно быть больше 0")
    except ValueError:
        raise ValueError("Неверный формат числа")
