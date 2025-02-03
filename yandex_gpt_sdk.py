import asyncio
import os.path
import json
import datetime
from typing import Dict, Any, List, Literal
from collections import deque
from yandex_cloud_ml_sdk import AsyncYCloudML

from utils import StorageManager
from config import YANDEX_FOLDER_ID, PATH_TO_SYSTEM_PROMPT, PATH_TO_BASE_USERS_INFO


active_user_GPT_session = {}


class ChatWithYandexGPT:
    def __init__(self, system_prompt: Dict[str, Any]):
        self.system_prompt = system_prompt

    def create_query(
            self,
            message: str,
            base_user_info: Dict[str, Any],
            type_message: Literal["general", "physical_activity", "nutrition"],
            last_responses: deque,
    ) -> List[Dict[str, str]]:
        query = [
            {"role": "system", "text": 'Базовая информация о пользователе' + json.dumps(base_user_info, ensure_ascii=False)},
            {"role": "system", "text": self.system_prompt.get(type_message, "")},
            {"role": "user", "text": message},
        ]
        if last_responses:
            query += last_responses
        return query

    @staticmethod
    async def send_message(model, message):
        result = await model.run(message)
        return result


class UserChatSession:
    def __init__(self, model, system_prompt, base_user_info, path_to_base_user_info):
        self.model = model
        self.system_prompt = system_prompt
        self.base_user_info = base_user_info
        self.path_to_base_user_info = path_to_base_user_info
        self.chat_instance = ChatWithYandexGPT(system_prompt)
        self.last_responses = deque(base_user_info.get('last_responses', []), maxlen=5)
        self.last_activity = datetime.datetime.now()

    @classmethod
    async def create(cls, model: AsyncYCloudML, path_to_system_prompt: str, path_to_base_user_info: str):
        system_prompt = await StorageManager.load_json(path_to_system_prompt)
        base_user_info = await StorageManager.load_json(path_to_base_user_info)
        return cls(model, system_prompt, base_user_info, path_to_base_user_info)

    async def save_session(self):
        self.base_user_info["last_responses"] = list(self.last_responses)
        await StorageManager.save_json(self.path_to_base_user_info, self.base_user_info)

    def handle_create_query(
            self, message: str,
            type_message: Literal["general", "physical_activity", "nutrition"]
    ) -> List[Dict[str, Any]]:

        query = self.chat_instance.create_query(
            message=message,
            base_user_info=self.base_user_info,
            type_message=type_message,
            last_responses=self.last_responses
        )
        return query

    async def handle_send_message(self, query: List[Dict[str, Any]]):
        response = await self.chat_instance.send_message(
            model=self.model,
            message=query,
        )
        self.last_responses.append({"role": "assistant", "text": response.alternatives[0].text})
        self.last_activity = datetime.datetime.now()
        return response


def start_model(temperature: float = 0.5, max_tokens: int = 20):
    sdk = AsyncYCloudML(
        folder_id=YANDEX_FOLDER_ID,
    )
    model = sdk.models.completions("yandexgpt")
    model = model.configure(temperature=temperature, max_tokens=max_tokens)
    return model


async def get_user_session(user_id: int, model: AsyncYCloudML):
    # global PATH_TO_SYSTEM_PROMPT, PATH_TO_BASE_USERS_INFO
    if user_id not in active_user_GPT_session:
        active_user_GPT_session[user_id] = await UserChatSession.create(
            model=model,
            path_to_system_prompt=PATH_TO_SYSTEM_PROMPT,
            path_to_base_user_info=os.path.join(PATH_TO_BASE_USERS_INFO, str(user_id) + '.json')
        )
    return active_user_GPT_session[user_id]


async def check_activity_session():
    """delay in seconds"""
    global active_user_GPT_session
    time_now = datetime.datetime.now()

    inactive_users = [
        user_id for user_id, session in active_user_GPT_session.items()
        if time_now - session.last_activity > datetime.timedelta(minutes=30)
    ]

    for user_id in inactive_users:
        await active_user_GPT_session[user_id].save_session()
        del active_user_GPT_session[user_id]


async def start_session_cleaner():
    while True:
        await check_activity_session()
        await asyncio.sleep(600)


async def main(message: str, type_message: str):
    model = start_model()
    chat = await get_user_session(user_id=1464672119, model=model)
    query = chat.handle_create_query(message=message, type_message=type_message)
    response = await chat.handle_send_message(query)
    print(response)
    return response


asyncio.run(main('Какая сегодня погода в Москве и какой сегодня день', "general"))
