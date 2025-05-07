import os
from uuid import uuid4

from yoomoney import Quickpay, Client


def create_invoice(amount: int) -> tuple[str, str]:
    uid = str(uuid4())
    quickpay = Quickpay(
        receiver=os.getenv("YOOMONEY_WALLET"),
        quickpay_form="shop",
        targets="Оплата подписки на канал",
        paymentType="SB",
        sum=amount,
        label=uid,
        successURL="https://t.me/EktbOplata_Bot"
    )
    return uid, quickpay.redirected_url,


def check_invoice(uid: str) -> bool:
    return True
    # client = Client(os.getenv("ACCESS_TOKEN"))
    # history = client.operation_history(label=uid)
    # if len(history.operations) == 0:
    #     return False
    # return history[0].status == "success"
