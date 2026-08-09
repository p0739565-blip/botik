"""
Сервис формирования счетов.

В этом файле нет никакой логики Telegram.
Он лишь получает тариф и возвращает данные,
необходимые для создания invoice.

Сейчас используется только Telegram Stars.

В будущем здесь появятся:

- build_card_invoice()
- build_crypto_invoice()
- refund_stars()
"""

from aiogram.types import LabeledPrice

STARS_CURRENCY = "XTR"


def build_stars_invoice(tariff: dict) -> dict:
    """
    Возвращает параметры для answer_invoice().
    """

    return {
        "title": f"Kopatych VPN • {tariff['title']}",
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
# Заготовки под будущие способы оплаты
# =====================================================

def build_card_invoice(tariff: dict):
    """
    Здесь позже будет создаваться счет
    через ЮKassa / CloudPayments / Stripe.
    """
    raise NotImplementedError


def build_crypto_invoice(tariff: dict):
    """
    Здесь позже будет CryptoBot/Cryptomus.
    """
    raise NotImplementedError