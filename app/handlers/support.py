from aiogram import F, Router
from aiogram.types import Message

from app.texts.messages import SUPPORT_TEXT

router = Router()


@router.message(F.text == "🆘 Поддержка")
async def support(message: Message):

    await message.answer(SUPPORT_TEXT)
