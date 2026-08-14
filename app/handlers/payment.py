from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    Message,
    PreCheckoutQuery,
)

from app.db import async_session
from app.keyboards.inline import payment_keyboard, payment_method_keyboard
from app.models import Payment
from app.services.payments import build_stars_invoice
from app.services.subscription import send_subscription
from app.services.users import get_or_create_user
from app.settings.tariffs import TARIFFS
from app.texts.messages import PAYMENT_THANKS_TEXT

router = Router()


# ==========================================
# Покупка подписки — сначала способ оплаты
# ==========================================

@router.message(F.text == "💳 Купить подписку")
async def buy_subscription(message: Message):

    await message.answer(
        "Выберите способ оплаты:",
        reply_markup=payment_method_keyboard(),
    )


@router.callback_query(F.data == "method_stars")
async def choose_stars_method(callback: CallbackQuery):

    await callback.answer()

    await callback.message.edit_text(
        "💎 Выберите тариф💎 :",
        reply_markup=payment_keyboard("stars"),
    )


@router.callback_query(F.data == "method_card")
async def choose_card_method(callback: CallbackQuery):

    await callback.answer()

    await callback.message.edit_text(
        "💎 Выберите тариф💎 :",
        reply_markup=payment_keyboard("card"),
    )


@router.callback_query(F.data == "payment_method_back")
async def back_to_payment_methods(callback: CallbackQuery):

    await callback.answer()

    await callback.message.edit_text(
        "Выберите способ оплаты:",
        reply_markup=payment_method_keyboard(),
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
# Банковская карта — оплата ещё не подключена
# ==========================================

@router.callback_query(F.data.startswith("buy_card_"))
async def buy_card(callback: CallbackQuery):

    await callback.answer(
        "Оплата картой скоро будет добавлена 🚀",
        show_alert=True,
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

    async with async_session() as session:
        session.add(
            Payment(
                user_id=user.id,
                tariff_key=tariff_key,
                method="stars",
                amount=message.successful_payment.total_amount,
                days=tariff["days"],
            )
        )
        await session.commit()

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