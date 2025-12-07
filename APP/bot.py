# bot.py - ВОССТАНАВЛИВАЕМ РАБОЧИЙ КОД
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import CommandStart

# ПРАВИЛЬНЫЕ ИМПОРТЫ
try:
    # Пробуем импортировать из config.py
    from config import TOKEN, PROXY_URL
except ImportError:
    # Если не получается, используем прямые значения
    TOKEN = "8478765106:AAEjPiQJpgXJ_er-5_U0U-HS6xVGwIbvrxU"
    PROXY_URL = "http://P89FcB:T6ot1M@170.246.55.245:9603"

# Импортируем остальные модули
try:
    from keyboards.main import main_keyboard
    from database.db import save_user_to_db, save_message_to_db
    from admin_panel import admin_router
    HAS_ADMIN = True
except ImportError as e:
    print(f"⚠️ Не удалось импортировать модули: {e}")
    HAS_ADMIN = False

async def main():
    # Создаем сессию с прокси
    session = AiohttpSession(proxy=PROXY_URL)
    bot = Bot(token=TOKEN, session=session)
    dp = Dispatcher()
    
    # Подключаем админку если есть
    if HAS_ADMIN:
        try:
            dp.include_router(admin_router)
            print("✅ Админка подключена")
        except Exception as e:
            print(f"⚠️ Ошибка подключения админки: {e}")
    
    # Команда /start
    @dp.message(CommandStart())
    async def cmd_start(message: Message):
        user_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        
        # Пробуем сохранить пользователя
        try:
            if 'save_user_to_db' in globals():
                save_user_to_db(user_id, username, first_name, last_name)
                save_message_to_db(user_id, '/start')
                print(f"✅ Пользователь {user_id} сохранен в БД")
        except Exception as e:
            print(f"⚠️ Не удалось сохранить в БД: {e}")
            # Бот продолжит работать
        
        await message.answer('Привет! 🎉')
        
        # Пробуем показать клавиатуру
        try:
            if 'main_keyboard' in globals():
                await message.answer(
                    text="Вот клавиатура:",
                    reply_markup=main_keyboard()
                )
        except Exception as e:
            await message.answer("Бот работает! (клавиатура не доступна)")
            print(f"⚠️ Ошибка клавиатуры: {e}")
    
    print("🤖 Бот запущен и готов к работе!")
    print(f"Токен: {TOKEN[:10]}...")
    print(f"Прокси: {PROXY_URL[:30]}...")
    
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())