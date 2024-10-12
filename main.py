import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import config
from app import database as db
from router import r
from script import date_check

# Bot token can be obtained via https://t.me/BotFather
# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()
dp.include_router(r)


async def on_startup() -> None:
    await db.db_start()


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    scheduler = AsyncIOScheduler(timezone=config.TIMEZONE)
    scheduler.add_job(date_check, "cron", hour="9", kwargs={"bot": bot})
    scheduler.start()

    # And the run events dispatching
    dp.startup.register(on_startup)
    await dp.start_polling(bot, skip_updates=False)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logging.info("Bot launched")
    asyncio.run(main())
    logging.info("Bot shut down")
