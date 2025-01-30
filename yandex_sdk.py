import asyncio
import aiofiles
import json
from typing import List, Literal, Optional, Dict, Any
from yandex_cloud_ml_sdk import YCloudML, AsyncYCloudML
from config import YANDEX_FOLDER_ID


def start_model():
    sdk = AsyncYCloudML(
        folder_id=YANDEX_FOLDER_ID,
    )
    model = sdk.models.completions("yandexgpt")
    model = model.configure(temperature=0.5)
    return model


class ChatWithYandexGPT:
    def __init__(self, system_prompt: Dict[str, Any], base_user_info: Dict[str, Any], path_to_base_user_info: str):
        self.path_to_base_user_info = path_to_base_user_info
        self.system_prompt = system_prompt
        self.base_user_info = base_user_info
        self.last_messages = self.base_user_info.get('last_messages', [])

    @staticmethod
    async def load_json(file_path: str) -> Dict[str, Any]:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            return json.loads(content)

    @classmethod
    async def create(cls, path_to_system_prompt: str, path_to_base_user_info: str):
        system_prompt = await cls.load_json(path_to_system_prompt)
        base_user_info = await cls.load_json(path_to_base_user_info)
        return cls(system_prompt, base_user_info, path_to_base_user_info)

    def create_message(
        self,
        message: str,
        type_message: Literal["general", "physical_activity", "nutrition"],
        first_message: Optional[bool] = False
    ) -> List[Dict[str, str]]:
        result = [
            {
                "role": "system",
                "text": self.base_user_info
            },
            {
                "role": "system",
                "text": self.system_prompt[type_message]
            },
            {
                "role": "user",
                "text": message,
            }
        ]
        if first_message:
            result += self.last_messages
        return result

    def add_message_in_dialogue(self, message: str):
        self.last_messages.append({"role": "assistant", "text": message})
        if len(self.last_messages) > 5:
            self.last_messages = self.last_messages[-5:]

    async def exit_from_chat(self):
        self.base_user_info['last_messages'] = self.last_messages
        async with aiofiles.open(self.path_to_base_user_info, "w") as f:
            json_data = json.dumps(self.base_user_info, indent=4)
            await f.write(json_data)


async def main(message):

    model = start_model()
    ChatWithYandexGPT()

    result = await model.run(message)
    print(f'{result.alternatives[0].text}')

    # print(f'{result=}')
    # print(f'{result[0]=}')
    # print(f'{result.alternatives[0].role=}')
    # print(f'{result.alternatives[0].text=}')
    # print(f'{result.alternatives[0].status=}')


asyncio.run(main())
