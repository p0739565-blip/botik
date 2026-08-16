"""
Приём callback'ов от Platega об изменении статуса транзакции.

URL для настройки в личном кабинете Platega (Настройки → Callback
URLs): {SUB_DOMAIN}/webhooks/platega

Документация: https://docs.platega.io/callback-об-изменении-статуса-транзакции

Важно: этот роутер живёт в процессе app.api (uvicorn), у которого нет
aiogram-диспетчера — только сам процесс бота (app.bot) его запускает.
Поэтому для отправки сообщения пользователю здесь заводится собственный
Bot(token=BOT_TOKEN); это два независимых клиента одного и того же
бота, Telegram Bot API это допускает.
"""

import logging

from aiogram import Bot
from fastapi import APIRouter, Request, Response
from sqlalchemy import select

from app.config import BOT_TOKEN, PLATEGA_MERCHANT_ID, PLATEGA_SECRET
from app.db import async_session
from app.models import Payment, PlategaPayment, User
from app.services.subscription import send_subscription_by_chat_id
from app.settings.tariffs import TARIFFS
from app.texts.messages import PAYMENT_THANKS_TEXT

logger = logging.getLogger("platega_webhook")

router = APIRouter()

# Отдельный Bot для уведомлений из вебхука — см. пояснение в шапке
# файла. Токен тот же, что у основного бота.
_notify_bot = Bot(token=BOT_TOKEN)

# Статусы, которые реально приходят от Platega (см. CallbackPayload).
STATUS_CONFIRMED = "CONFIRMED"
STATUS_CANCELED = "CANCELED"
STATUS_CHARGEBACKED = "CHARGEBACKED"


@router.post("/webhooks/platega")
async def platega_webhook(request: Request):

    # Platega подписывает запрос теми же двумя заголовками, что и мы
    # используем для авторизации своих запросов к их API.
    if (
        request.headers.get("X-MerchantId") != PLATEGA_MERCHANT_ID
        or request.headers.get("X-Secret") != PLATEGA_SECRET
    ):
        logger.warning("platega webhook: bad X-MerchantId/X-Secret")
        return Response(status_code=401)

    data = await request.json()

    transaction_id = data.get("id")
    status = data.get("status")

    if not transaction_id or not status:
        logger.warning("platega webhook: malformed payload %r", data)
        return Response(status_code=400)

    async with async_session() as session:
        result = await session.execute(
            select(PlategaPayment).where(
                PlategaPayment.transaction_id == transaction_id
            )
        )
        payment = result.scalar_one_or_none()

        if payment is None:
            # Неизвестная транзакция — либо чужая, либо была создана
            # раньше миграции. Отвечаем 200, чтобы Platega не долбила
            # повторами (см. до 3 ретраев каждые 5 минут).
            logger.warning(
                "platega webhook: unknown transaction_id=%s", transaction_id
            )
            return {"ok": True}

        if payment.status in (STATUS_CONFIRMED, STATUS_CANCELED, STATUS_CHARGEBACKED):
            # Уже обработан — Platega могла прислать callback повторно.
            return {"ok": True}

        payment.status = status
        user_id = payment.user_id
        chat_id = payment.chat_id
        tariff_key = payment.tariff_key
        amount = payment.amount
        method = payment.method or "card"

        await session.commit()

        if status == STATUS_CONFIRMED:
            user_result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()

    if status != STATUS_CONFIRMED:
        # CANCELED — платёж не прошёл, пользователь и так видит это на
        # странице оплаты. CHARGEBACKED — возврат по уже выданной
        # подписке; отмена доступа для MVP делается вручную из админки,
        # чтобы не рвать доступ на автомате при спорных возвратах.
        return {"ok": True}

    if user is None:
        logger.error(
            "platega webhook: user_id=%s not found for transaction_id=%s",
            user_id,
            transaction_id,
        )
        return {"ok": True}

    tariff = TARIFFS.get(tariff_key)

    if tariff is None:
        logger.error(
            "platega webhook: unknown tariff_key=%s for transaction_id=%s",
            tariff_key,
            transaction_id,
        )
        return {"ok": True}

    async with async_session() as session:
        session.add(
            Payment(
                user_id=user_id,
                tariff_key=tariff_key,
                method=method,
                amount=amount,
                days=tariff["days"],
            )
        )
        await session.commit()

    try:
        await _notify_bot.send_message(chat_id, PAYMENT_THANKS_TEXT)
        await send_subscription_by_chat_id(
            _notify_bot,
            chat_id,
            user,
            tariff["days"],
        )
    except Exception:
        # Если здесь упадёт (например, пользователь заблокировал бота),
        # важно не ронять обработку callback'а — Platega ждёт 200 в
        # течение 60 секунд и иначе будет ретраить.
        logger.exception(
            "platega webhook: failed to notify chat_id=%s", chat_id
        )

    return {"ok": True}
