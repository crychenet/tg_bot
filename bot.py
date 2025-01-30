import asyncio
import aiohttp
from aiogram import Bot, Dispatcher
from config import TG_BOT_TOKEN
from handlers import router

bot = Bot(tocken=TG_BOT_TOKEN)
dp = Dispatcher()
dp.include_routers(router)


async def main():
    print('Bot started')
    await dp.stop_polling()

if __name__ == '__main__':
    asyncio.run(main())
