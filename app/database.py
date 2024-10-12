from datetime import datetime, timedelta

import sqlite3 as sq
from aiogram.types import User


db = sq.connect("app/test.db")
cur = db.cursor()


async def db_start() -> None:
    cur.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER NOT NULL PRIMARY KEY, name TEXT, "
                "sub_start TEXT, sub_end TEXT);")
    db.commit()


async def check_user(user_id: int) -> None:
    cur.execute(f"SELECT user_id FROM users WHERE user_id = {user_id} LIMIT 1;")
    return cur.fetchone()


async def add_user(user: User, start, span) -> None:
    if not await check_user(user.id):
        cur.execute(f"INSERT INTO users VALUES ({user.id}, '{user.full_name}', '{start}', "
                    f"'{start + timedelta(weeks=4 * span)}');")
    else:
        sub_end = datetime.strptime(
            str(cur.execute(f"SELECT sub_end FROM users WHERE user_id = {user.id} LIMIT 1;").fetchone()[0]),
            "%Y-%m-%d %H:%M:%S.%f"
        )
        cur.execute(f"UPDATE users SET sub_end = '{sub_end + timedelta(weeks=4 * span)}' WHERE user_id = {user.id};")
    db.commit()


async def check_expiration() -> tuple[list, list]:
    cur.execute("SELECT user_id, name FROM users WHERE julianday(sub_end) - julianday(datetime()) <= 0;")
    to_remove = cur.fetchall()

    cur.execute(f"DELETE FROM users WHERE julianday(sub_end) - julianday(datetime()) <= 0;")
    db.commit()

    cur.execute(
        "SELECT user_id, sub_end FROM users WHERE julianday(sub_end) - julianday(datetime()) <= 3 AND "
        "julianday(sub_end) - julianday(datetime()) > 0;"
    )
    to_remind = cur.fetchall()

    return to_remove, to_remind
