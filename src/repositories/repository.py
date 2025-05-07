from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from aiogram.types import User as TgUser, Message
from sqlalchemy import select, delete, func, Sequence, Row
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User, Plan


class SubBotRepository(ABC):
    @abstractmethod
    async def get_user(self, tg_user: TgUser):
        pass

    @abstractmethod
    async def add_user(self, user: TgUser):
        pass

    @abstractmethod
    async def add_subscription(self, user: TgUser, start, days):
        pass

    @abstractmethod
    async def check_expiration(self, date):
        pass

    @abstractmethod
    async def clear_plans(self):
        pass

    @abstractmethod
    async def add_plan(self, message: Message):
        pass

    @abstractmethod
    async def get_plan(self, plan_id):
        pass

    @abstractmethod
    async def get_all_plans(self):
        pass


class SQLAlchemySubBotRepository(SubBotRepository):
    def __init__(self, database: AsyncSession):
        self.db = database

    async def get_user(self, tg_user: TgUser) -> Row[tuple[User]] | None:
        result = await self.db.execute(select(User).where(User.tg_id == tg_user.id))
        user = result.first()

        return user

    async def add_user(self, user: TgUser) -> None:
        if await self.get_user(user) is None:
            new_user = User(
                tg_id=user.id,
                username=user.username,
                fullname=user.full_name,
                sub_start=None,
                sub_end=None,
                sub_active=False,
            )
            self.db.add(new_user)
            await self.db.commit()

    async def add_subscription(self, user: TgUser, date, span) -> None:
        await self.add_user(user)

        tg_id = user.id
        user = await self.db.scalar(select(User).where(User.tg_id == tg_id))
        if user.sub_active:
            user.sub_end += timedelta(days=span)
        else:
            user.sub_start = date
            user.sub_end = date + timedelta(days=span)
            user.sub_active = True
        await self.db.commit()

    async def check_expiration(self, date) -> tuple[Sequence[Row[tuple[User]]], Sequence[Row[tuple[User]]]]:
        # fetch expired users and set their "sub_active" field to False
        query_to_remove = await self.db.execute(select(User).where(User.sub_end <= date))
        to_remove = query_to_remove.all()

        for expired_user in to_remove:
            expired_user.sub_active = False
        await self.db.commit()

        # fetch users that are 3 and fewer days away from expiration but not expired
        query_to_remind = await self.db.execute(
            select(User).where(date < User.sub_end, User.sub_end <= date + timedelta(days=3))
        )
        to_remind = query_to_remind.all()

        return to_remove, to_remind

    async def clear_plans(self) -> None:
        try:
            await self.db.execute(delete(Plan))
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            print(f'Error clearing plans: {e}')

    async def add_plan(self, message: Message) -> None:
        rates = message.text.split('\n')
        rates = list(map(lambda x: Plan(days=int(x.split(':')[0]), price=int(x.split(':')[1])), rates))
        for rate in rates:
            self.db.add(rate)
        await self.db.commit()

    async def get_plan(self, plan_id) -> Row[tuple[Plan]]:
        query_plan = await self.db.execute(select(Plan).where(Plan.id == plan_id))
        plan = query_plan.first()

        return plan

    async def get_all_plans(self) -> Sequence[Row[tuple[Plan]]]:
        query_plans = await self.db.execute(select(Plan))
        plans = query_plans.all()

        return plans
