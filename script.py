import time
from datetime import datetime
from math import ceil

from aiogram import Bot, html

import config
from app import database as db


async def date_check(bot: Bot) -> None:
    admins = await bot.get_chat_administrators(chat_id=config.CHANNEL_ID)
    to_remove, to_remind = await db.check_expiration()

    for user in to_remove:
        await bot.ban_chat_member(config.CHANNEL_ID, user[0], until_date=int(ceil(time.time())) + 30)
        await bot.send_message(user[0], "You've been removed from the channel as your subscription has expired")

        for admin in admins:
            if not admin.user.is_bot:
                await bot.send_message(
                    admin.user.id,
                    f"User {html.bold(user[1])} (@{user.username}, id: {user.id}) "
                    f"has been removed from the channel as their subscription expired"
                )

    for user in to_remind:
        sub_end = datetime.strptime(user[1], "%Y-%m-%d %H:%M:%S.%f")
        delta = sub_end - datetime.now()
        await bot.send_message(user[0], f"Your subscription to the channel will expire in {delta.days} "
                                        f"{'day' if delta.days == 1 else 'days'}! "
                                        f"(Deadline is {sub_end.day}.{sub_end.month}.{sub_end.year})")
        # add an inline button to commit a payment
