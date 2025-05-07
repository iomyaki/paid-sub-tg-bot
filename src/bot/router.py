import logging
from datetime import datetime, timedelta

from aiogram import Bot, Router, F, html
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, ContentType, CallbackQuery

from src.bot import kb
from src.bot.payment import create_invoice, check_invoice
from src.core.config import settings
from src.db import AsyncSessionLocal
from src.repositories.repository import SubBotRepository, SQLAlchemySubBotRepository

r = Router()


class Form(StatesGroup):
    upload_new_plans = State()


async def get_repo() -> SubBotRepository:
    async with AsyncSessionLocal() as session:
        return SQLAlchemySubBotRepository(session)


@r.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    repo: SubBotRepository = await get_repo()

    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}! "
                         f"Here you can buy a subscription to the private channel. "
                         f"Select a subscription plan below:", reply_markup=await kb.plans(repo))
    await repo.add_user(message.from_user)


@r.callback_query(kb.PlanData.filter())
async def plan(c: CallbackQuery, bot: Bot, callback_data: kb.PlanData) -> None:
    repo: SubBotRepository = await get_repo()

    plan_ = await repo.get_plan(callback_data.id)

    if settings.PAYMENTS_TOKEN.split(':')[1] == 'TEST':
        await c.answer("It's a test payment!")

    await bot.send_invoice(
        chat_id=c.from_user.id,
        title="Bot subscription",
        description=f"Activation of the channel subscription for {plan_[0].days} days",
        payload="test_payload",
        currency="rub",
        prices=[LabeledPrice(label="test sub", amount=plan_[0].price * 100)],
        message_thread_id=None,
        provider_token=settings.PAYMENTS_TOKEN,
        start_parameter=f"{plan_[0].days}-days-subscription",
        is_flexible=False
    )


@r.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot) -> None:
    """
    Pre-checkout: must be answered in 10 seconds
    """

    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@r.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: Message, bot: Bot) -> None:
    """
    Successful payment
    """

    repo: SubBotRepository = await get_repo()

    now = datetime.now()
    user = message.from_user
    user_db = await repo.get_user(user)
    admins = await bot.get_chat_administrators(chat_id=settings.CHANNEL_ID)

    logging.info('SUCCESSFUL PAYMENT')
    logging.info(message.successful_payment)
    msg = f'Payment {message.successful_payment.total_amount / 100} {message.successful_payment.currency} succeeded!'

    await message.answer(msg)
    if not user_db[0].sub_active:
        expiration_date = now + timedelta(minutes=5)
        link = await bot.create_chat_invite_link(
            chat_id=settings.CHANNEL_ID,
            name='Invitation to the private channel',
            expire_date=expiration_date,
            member_limit=1,
            creates_join_request=False
        )
        await message.answer(
            f'Your invitation to the private channel (expires in 5 minutes):\n{link.invite_link}',
            protect_content=True,
        )
    else:
        await message.answer('Your subscription has been extended!')
    await repo.add_subscription(user, now, 1)  # TEMPORARY hardcoded period of time for testing

    for admin in admins:
        if not admin.user.is_bot:
            await bot.send_message(
                admin.user.id,
                f'User {html.bold(user.full_name)} (@{user.username}, id: {user.id}) '
                'has just bought a subscription to the private channel!'
            )


@r.message(Command('setup'))
async def setup(message: Message, bot: Bot, state: FSMContext):
    admins = await bot.get_chat_administrators(chat_id=settings.CHANNEL_ID)
    admins_set = set()
    for admin in admins:
        admins_set.add(admin.user.id)
    if message.from_user.id not in admins_set:
        await message.answer("Only channel's admins are allowed to change subscription plans")
        return

    await state.set_state(Form.upload_new_plans)
    await message.answer("""Load new plans for the private chat in this format:

amount of days:price
amount of days:price
amount of days:price
(in one message)

For example:

1:100
7:200
14:300
28:500

The answer above will create 4 plans:
- 1 day for 100 ¤;
- 7 days for 200 ¤;
- 14 days for 300 ¤;
- 28 days for 500 ¤.

All old plans will be deleted once you confirm new ones.

To exit, send a /cancel command.""")


@r.message(Form.upload_new_plans, Command("cancel"))
async def cancel_state(message: Message, state: FSMContext):
    await message.answer("Uploading new plans has been cancelled")
    await state.clear()


@r.message(Form.upload_new_plans)
async def new_rates(message: Message, state: FSMContext):
    repo: SubBotRepository = await get_repo()
    try:
        await repo.clear_plans()
        await repo.add_plan(message)
    except Exception as e:
        logging.warning(e)
        await message.answer("Incorrect format, please try again")
    else:
        await message.answer("✅ Plans have been successfully updated!")
        await state.clear()
