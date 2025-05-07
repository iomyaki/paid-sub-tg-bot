import asyncio
import logging
import sys
import tzlocal

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.core.config import settings
from src.bot.router import r
from src.bot.script import date_check

dp = Dispatcher()
dp.include_router(r)


#async def on_startup() -> None:
    #await db.db_start()


async def main() -> None:
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    scheduler = AsyncIOScheduler(timezone=str(tzlocal.get_localzone()))
    #scheduler.add_job(date_check, "cron", hour="9", kwargs={"bot": bot})
    scheduler.add_job(date_check, "cron", second="20", kwargs={"bot": bot})
    scheduler.start()

    #dp.startup.register(on_startup)
    await dp.start_polling(bot, skip_updates=False)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logging.info("Bot launched")
    asyncio.run(main())
    logging.info("Bot shut down")
