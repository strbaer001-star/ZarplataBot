import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers import router
from database import init_db
from scheduler import start_scheduler

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    await init_db()
    await start_scheduler(bot)

    print("✅ Бот Зарплата Щодня запущено!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
