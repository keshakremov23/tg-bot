from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

async def main_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    buttons = [
        ("Кнопка 1", "btn1"),
        ("Кнопка 2", "btn2"),
        ("Кнопка 3", "btn3"),
        ("Кнопка 4", "btn4"),
        ("Кнопка 5", "btn5"),
    ]
    
    for text, callback_data in buttons:
        builder.add(types.InlineKeyboardButton(
            text=text,
            callback_data=callback_data
        ))
    
    builder.adjust(2)  # 2 кнопки в ряд
    return builder.as_markup()