import logging
from datetime import datetime, timedelta

from aiogram import Bot, Router, F, html
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, ContentType

import config
from app import database as db
from app import kb

r = Router()
PRICE = LabeledPrice(label="Sub month", amount=100 * 100)  # 100 roubles times 100 (kopecks)


@r.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with '/start' command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}! "
                         f"Here you can buy a subscription to the private channel", reply_markup=kb.buy())


# buy
# https://stackoverflow.com/questions/77876174/aiogram3-3-0-does-not-send-payment-send-invoice
@r.message(F.text.lower() == "subscribe")
async def buy(message: Message, bot: Bot) -> None:
    if config.PAYMENTS_TOKEN.split(":")[1] == "TEST":
        await message.answer("It's a test payment!")

    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Bot subscription",
        description="Активация подписки на канал на 1 месяц",
        payload="test_payload",
        currency="rub",
        prices=[PRICE],
        message_thread_id=None,
        provider_token=config.PAYMENTS_TOKEN,
        start_parameter="one-month-subscription",
        is_flexible=False
    )


# pre checkout (must be answered in 10 seconds)
@r.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot) -> None:
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


# successful payment
@r.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: Message, bot: Bot) -> None:
    user = message.from_user
    admins = await bot.get_chat_administrators(chat_id=config.CHANNEL_ID)

    logging.info(f"SUCCESSFUL PAYMENT")
    logging.info(message.successful_payment)
    msg = f"Платёж {message.successful_payment.total_amount // 100} {message.successful_payment.currency} успешен!"

    expiration_date = datetime.now() + timedelta(minutes=5)
    link = await bot.create_chat_invite_link(
        chat_id=config.CHANNEL_ID,
        name="Invitation to the private channel",
        expire_date=expiration_date,
        member_limit=1,
        creates_join_request=False
    )

    await message.answer(msg)
    await message.answer(f"Your invitation to the private channel (expires in 5 minutes):\n{link.invite_link}")
    await db.add_user(user, datetime.now(), 1)

    for admin in admins:
        if not admin.user.is_bot:
            await bot.send_message(
                admin.user.id,
                f"User {html.bold(user.full_name)} (@{user.username}, id: {user.id}) "
                f"has just bought a subscription to the private channel!"
            )


"""@r.message()
async def echo_handler(message: Message) -> None:
    # Handler will forward receive a message back to the sender
    # By default, message handler will handle all message types (like a text, photo, sticker etc.)
    try:
        # Send a copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")"""
