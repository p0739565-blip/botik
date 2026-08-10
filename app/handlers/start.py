from aiogram import Bot, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.keyboards.inline import channel_keyboard
from app.keyboards.reply import main_menu
from app.services.users import get_or_create_user, is_subscribed
from app.texts.messages import NEED_CHANNEL_SUB_TEXT, WELCOME_TEXT

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    user = await get_or_create_user(message.from_user.id, message.from_user.username)

    if not await is_subscribed(bot, message.from_user.id):
        await message.answer(
            NEED_CHANNEL_SUB_TEXT,
            reply_markup=channel_keyboard(),
        )
        return

    await message.answer(
        WELCOME_TEXT,
        reply_markup=main_menu()
    )
