import asyncio
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.session.aiohttp import AiohttpSession

TOKEN = "#####"

PROXY_URL = "######"

async def main():
    session = AiohttpSession(proxy=PROXY_URL)
    bot = Bot(token=TOKEN, session=session)
    dp = Dispatcher()
    @dp.message(F.text == 'ку')
    async def cmd_start(message: Message):
        await message.answer('ку')

    print("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())