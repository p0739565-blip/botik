from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.config import CHANNEL_USERNAME
from app.settings.tariffs import TARIFFS


# ==========================
# Кнопка подписки на канал
# ==========================

def channel_keyboard() -> InlineKeyboardMarkup:

    buttons = []

    if CHANNEL_USERNAME:
        buttons.append([
            InlineKeyboardButton(
                text="📢 Открыть канал",
                url=f"https://t.me/{CHANNEL_USERNAME}",
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="✅ Я подписался",
            callback_data="check_sub",
        )
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )


# ==========================
# Клавиатура покупки
# ==========================

def payment_keyboard(payment_type: str = "stars") -> InlineKeyboardMarkup:

    keyboard = []

    for key, tariff in TARIFFS.items():

        # Пробный тариф не продаётся
        if tariff.get("is_trial"):
            continue

        if payment_type == "stars":
            price = tariff["stars"]
            suffix = f"⭐ {price}"

        elif payment_type == "card":
            price = tariff["card"]

            if price is None:
                continue

            suffix = f"{price} ₽"

        elif payment_type == "crypto":
            price = tariff["crypto"]

            if price is None:
                continue

            suffix = f"{price} USDT"

        else:
            continue

        keyboard.append([
            InlineKeyboardButton(
                text=f"{tariff['title']} — {suffix}",
                callback_data=f"buy_{payment_type}_{key}",
            )
        ])

    # Пока доступны только Stars
    if payment_type == "stars":

        keyboard.append([
            InlineKeyboardButton(
                text="💳 Банковская карта (скоро)",
                callback_data="soon",
            )
        ])

        keyboard.append([
            InlineKeyboardButton(
                text="₿ Криптовалюта (скоро)",
                callback_data="soon",
            )
        ])

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )
# ==========================
# Клавиатура документов
# ==========================

def documents_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📄 Политика конфиденциальности",
                    url="https://telegra.ph/Politika-konfidencialnosti-08-08-87",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📄 Пользовательское соглашение",
                    url="https://telegra.ph/Polzovatelskoe-soglashenie-08-08-51",
                )
            ],
        ]
    )