# keyboards/main_kb.py
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

def zxc():
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Кнопка 1",
            callback_data="btn1"
        ),
        types.InlineKeyboardButton(
            text="Кнопка 2", 
            callback_data="btn2"
        ),
        types.InlineKeyboardButton(
            text="Кнопка 3",
            callback_data="btn3"
        ),
        types.InlineKeyboardButton(
            text="Кнопка 4",
            callback_data="btn4"
        ),
        types.InlineKeyboardButton(
            text="Кнопка 5",
            callback_data="btn5"
        )
    )
    
    return builder.as_markup()