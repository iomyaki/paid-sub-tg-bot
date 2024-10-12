from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def buy() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Subscribe")]],
        resize_keyboard=True
    )
