import asyncio
import os.path
import json
import datetime
import sys
from typing import Dict, Any, List, Literal
from collections import deque
from yandex_cloud_ml_sdk import AsyncYCloudML

from utils import StorageManager
from config import YANDEX_FOLDER_ID, PATH_TO_SYSTEM_PROMPT, PATH_TO_BASE_USERS_INFO, YANDEX_SDK_MODEL



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


class SessionManager:
    _instances = None

    def __new__(cls):
        if cls._instances is None:
            cls._instances = super(SessionManager, cls).__new__(cls)
            cls._instances.active_sessions = {}
        return cls._instances

    async def get_user_session(self, user_id: int):
        if user_id not in self.active_sessions:
            self.active_sessions[user_id] = await UserChatSession.create(
                model=YANDEX_SDK_MODEL,
                path_to_system_prompt=PATH_TO_SYSTEM_PROMPT,
                path_to_base_user_info=os.path.join(PATH_TO_BASE_USERS_INFO, f"{user_id}.json"),
            )
        return self.active_sessions[user_id]

    async def remove_inactive_sessions(self):
        time_now = datetime.datetime.now()
        inactive_users = [
            user_id for user_id, session in self.active_sessions.items()
            if time_now - session.last_activity > datetime.timedelta(minutes=30)
        ]
        for user_id in inactive_users:
            await self.active_sessions[user_id].save_session()
            del self.active_sessions[user_id]

    def get_active_sessions(self) -> Dict[int, UserChatSession]:
        return self.active_sessions


async def main(message: str, type_message: str):
    sessions = SessionManager()
    session = await sessions.get_user_session(1464672119)
    query = session.handle_create_query(message, type_message)
    result = await session.handle_send_message(query)
    print(result)


asyncio.run(main('Ты крутой?', "general"))
