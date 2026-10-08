import asyncio
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers.start import router as start_router
from handlers.menu import router as menu_router
from database import create_database


load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()

dp.include_router(start_router)
dp.include_router(menu_router)


async def main():
    create_database()
    bot = Bot(token=TOKEN)

    print("Бот запущен!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())