"""
Сервис формирования счетов.

Telegram Stars собирается локально (build_stars_invoice). Оплата
картой уходит во внешний платёжный шлюз Platega (create_card_payment) —
в отличие от Stars, эта транзакция асинхронна: мы получаем ссылку на
оплату сразу, а факт оплаты приходит позже отдельным вебхуком
(app.api:platega_webhook), поэтому здесь же заводится запись
PlategaPayment для сопоставления вебхука с пользователем и тарифом.

В будущем здесь появится:

- build_crypto_invoice()
- refund_stars()
"""

from aiogram.types import LabeledPrice

from app.config import PLATEGA_CARD_METHOD, SUB_DOMAIN
from app.db import async_session
from app.models import PlategaPayment, User
from app.services import platega

STARS_CURRENCY = "XTR"


def build_stars_invoice(tariff: dict) -> dict:
    """
    Возвращает параметры для answer_invoice().
    """

    return {
        "title": f"Маквин VPN • {tariff['title']}",
        "description": f"Подписка на {tariff['days']} дней",
        "currency": STARS_CURRENCY,
        "prices": [
            LabeledPrice(
                label=tariff["title"],
                amount=tariff["stars"],
            )
        ],
    }


# =====================================================
# Банковская карта — Platega
# =====================================================

async def create_card_payment(
    user: User,
    chat_id: int,
    tariff_key: str,
    tariff: dict,
) -> str:
    """
    Создаёт транзакцию в Platega и локальную запись PlategaPayment
    (status=PENDING), возвращает ссылку на страницу оплаты.

    Подтверждение оплаты придёт отдельно, через POST на
    /webhooks/platega — там и выдаётся подписка.
    """

    amount = tariff["card"]

    response = await platega.create_transaction(
        amount=amount,
        currency="RUB",
        description=f"Kopatych VPN — {tariff['title']}",
        return_url=f"{SUB_DOMAIN}/payments/platega/return",
        failed_url=f"{SUB_DOMAIN}/payments/platega/failed",
        payload=f"user:{user.tg_id}:tariff:{tariff_key}",
        payment_method=PLATEGA_CARD_METHOD,
    )

    transaction_id = response["transactionId"]

    # v1 отдаёт ссылку в поле "redirect", более новый v2-эндпоинт —
    # в "url". Проверяем оба, чтобы не сломаться при смене API.
    redirect_url = response.get("redirect") or response.get("url")

    if not redirect_url:
        raise platega.PlategaError(200, f"Нет ссылки на оплату в ответе: {response}")

    async with async_session() as session:
        session.add(
            PlategaPayment(
                user_id=user.id,
                chat_id=chat_id,
                transaction_id=transaction_id,
                tariff_key=tariff_key,
                amount=amount,
                currency="RUB",
                status="PENDING",
            )
        )
        await session.commit()

    return redirect_url


# =====================================================
# Заготовки под будущие способы оплаты
# =====================================================

def build_crypto_invoice(tariff: dict):
    """
    Здесь позже будет CryptoBot/Cryptomus.
    """
    raise NotImplementedError