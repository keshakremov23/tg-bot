# APP/bot.py
import asyncio
import sys
import os

# Добавляем родительскую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import CommandStart

from keyboards.main_kb import zxc
from database.db import save_user_to_db, save_message_to_db
from admin_panel import admin_router  # Теперь импорт должен работать

TOKEN = "8478765106:AAEjPiQJpgXJ_er-5_U0U-HS6xVGwIbvrxU"
PROXY_URL = "http://P89FcB:T6ot1M@170.246.55.245:9603"

async def main():
    session = AiohttpSession(proxy=PROXY_URL)
    bot = Bot(token=TOKEN, session=session)
    dp = Dispatcher()
    
    # Подключаем админ-роутер
    dp.include_router(admin_router)
    
    # команда /start для всех
    @dp.message(CommandStart())
    async def cmd_start(message: Message):
        user_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        
        save_user_to_db(user_id, username, first_name, last_name)
        save_message_to_db(user_id, '/start')
        
        await message.answer('Привет!')
        await message.answer(
            text="Вот клавиатура:",
            reply_markup=zxc()
        )
    
    print("Бот запущен и готов к работе")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())