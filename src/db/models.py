from datetime import datetime
from typing import List

from sqlalchemy import TIMESTAMP, Integer, BigInteger, String, Boolean, func, ForeignKey
from sqlalchemy.orm import (
    declared_attr,
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
    )

    @declared_attr
    def __tablename__(self) -> str:
        return self.__name__.lower() + "s"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id}, created_at={self.created_at}, updated_at={self.updated_at})>"


class User(Base):
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    fullname: Mapped[str] = mapped_column(String(100), nullable=False)
    sub_start: Mapped[datetime | None] = mapped_column(TIMESTAMP, default=None)
    sub_end: Mapped[datetime | None] = mapped_column(TIMESTAMP, default=None)
    sub_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}(id={self.id}, created_at={self.created_at}, updated_at={self.updated_at}, "
            f"tg_id={self.tg_id}, username={self.username}, fullname={self.fullname}, sub_start={self.sub_start}, "
            f"sub_end={self.sub_end}, sub_active={self.sub_active})>"
        )


class Plan(Base):
    days: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}(id={self.id}, created_at={self.created_at}, updated_at={self.updated_at}, "
            f"days={self.days}, price={self.price})>"
        )
