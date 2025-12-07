from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.services.user import UserService
from app.keyboards.main import main_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    # Сохраняем пользователя
    await UserService.save_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    # Сохраняем сообщение
    await UserService.save_message(
        user_id=message.from_user.id,
        message_text='/start'
    )
    
    # Отправляем приветствие
    await message.answer('Привет!')
    await message.answer(
        text="Вот клавиатура:",
        reply_markup=await main_keyboard()
    )