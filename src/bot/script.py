import time
import tzlocal
from datetime import datetime
from math import ceil

from aiogram import Bot, html

from src.bot import kb
from src.core.config import settings
from src.db import AsyncSessionLocal
from src.repositories.repository import SubBotRepository, SQLAlchemySubBotRepository


async def get_repo() -> SubBotRepository:
    async with AsyncSessionLocal() as session:
        return SQLAlchemySubBotRepository(session)


async def date_check(bot: Bot) -> None:
    repo = await get_repo()

    now = datetime.now()
    admins = await bot.get_chat_administrators(chat_id=settings.CHANNEL_ID)
    to_remove, to_remind = await repo.check_expiration(now)

    for user in to_remove:
        await bot.ban_chat_member(settings.CHANNEL_ID, user.tg_id, until_date=int(ceil(time.time())) + 30)
        await bot.send_message(user.tg_id, "You've been removed from the channel as your subscription has expired")

        for admin in admins:
            if not admin.user.is_bot:
                await bot.send_message(
                    admin.user.id,
                    f"User {html.bold(user.fullname)} (@{user.username}, ID: {user.tg_id}) "
                    f"has been removed from the channel as their subscription has expired"
                )

    for user in to_remind:
        user = user[0]
        sub_end = user.sub_end
        sub_end_day = str(sub_end.day).zfill(2)
        sub_end_month = str(sub_end.month).zfill(2)
        delta = sub_end - now
        await bot.send_message(user.tg_id, f"Your subscription to the channel will expire in {html.bold(delta.days)} "
                                           f"{html.bold('day' if delta.days == 1 else 'days')}! "
                                           f"Deadline is {html.bold(sub_end_day)}.{html.bold(sub_end_month)}."
                                           f"{html.bold(sub_end.year)} ({tzlocal.get_localzone()}).\n\n"
                                           f"You can extend your subscription now:", reply_markup=await kb.plans(repo))
