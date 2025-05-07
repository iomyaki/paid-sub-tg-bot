from aiogram import Bot
from aiogram.filters.callback_data import CallbackData
from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from src.repositories.repository import SubBotRepository, SQLAlchemySubBotRepository

"""def buy() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Subscribe")]],
        resize_keyboard=True
    )"""


class PlanData(CallbackData, prefix='plan'):
    id: int


class PayData(CallbackData, prefix='pay'):
    uid: str
    days: int


async def plans(repo: SubBotRepository) -> InlineKeyboardMarkup:
    data = await repo.get_all_plans()
    markup = InlineKeyboardBuilder()
    for plan in data:
        plan = plan[0]
        markup.button(text=f'{plan.days} days for {plan.price} ¤', callback_data=PlanData(id=plan.id).pack())
    markup.adjust(1)

    return markup.as_markup()


def pay(link: str, uid: str, days: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Pay', url=link)],
            [InlineKeyboardButton(text='Check payment', callback_data=PayData(uid=uid, days=days).pack())]
        ]
    )
