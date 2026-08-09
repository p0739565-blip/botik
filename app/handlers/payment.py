from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    Message,
    PreCheckoutQuery,
)

from app.keyboards.inline import payment_keyboard
from app.services.payments import build_stars_invoice
from app.services.subscription import send_subscription
from app.services.users import get_or_create_user
from app.settings.tariffs import TARIFFS
from app.texts.messages import PAYMENT_THANKS_TEXT

router = Router()


# ==========================================
# Покупка подписки
# ==========================================

@router.message(F.text == "💳 Купить подписку")
async def buy_subscription(message: Message):

    await message.answer(
        "💎 Выберите тариф:",
        reply_markup=payment_keyboard(),
    )


# ==========================================
# Telegram Stars
# ==========================================

@router.callback_query(F.data.startswith("buy_stars_"))
async def buy_stars(callback: CallbackQuery):

    tariff_key = callback.data.removeprefix("buy_stars_")

    tariff = TARIFFS.get(tariff_key)

    if tariff is None:
        await callback.answer(
            "Тариф не найден.",
            show_alert=True,
        )
        return

    invoice = build_stars_invoice(tariff)

    await callback.answer()

    await callback.message.answer_invoice(
        provider_token="",
        payload=f"subscription:{tariff_key}",
        **invoice,
    )


# ==========================================
# Проверка оплаты
# ==========================================

@router.pre_checkout_query()
async def pre_checkout(
    pre_checkout_query: PreCheckoutQuery,
):

    await pre_checkout_query.answer(ok=True)


# ==========================================
# Оплата успешна
# ==========================================

@router.message(F.successful_payment)
async def successful_payment(message: Message):

    payload = message.successful_payment.invoice_payload

    tariff_key = payload.replace(
        "subscription:",
        "",
    )

    tariff = TARIFFS.get(tariff_key)

    if tariff is None:
        await message.answer(
            "Ошибка тарифа."
        )
        return

    user = await get_or_create_user(
        message.from_user.id,
        message.from_user.username,
    )

    await send_subscription(
        message,
        user,
        tariff["days"],
    )

    await message.answer(
        PAYMENT_THANKS_TEXT
    )


# ==========================================
# Пока недоступно
# ==========================================

@router.callback_query(F.data == "soon")
async def soon(callback: CallbackQuery):

    await callback.answer(
        "Этот способ оплаты скоро появится 🚀",
        show_alert=True,
    )