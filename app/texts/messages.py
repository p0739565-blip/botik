"""Тексты сообщений бота — собраны в одном месте, чтобы не искать
формулировки по всем handlers/*.py."""

NEED_CHANNEL_SUB_TEXT = (
    "Привет! Чтобы получить доступ, подпишись на наш канал "
    "и нажми «Я подписался»."
)

WELCOME_TEXT = (
    "👋 Добро пожаловать в Makwin\n\n"
    "Быстрый и стабильный.\n\n"
    "Выберите действие:"
)

NOT_SUBSCRIBED_ALERT = "Ты пока не подписан на канал 🙁"

ALREADY_HAS_SUBSCRIPTION_TEXT = (
    "У вас уже есть подписка.\n"
    "Используйте кнопку 💳 Купить подписку для продления."
)

INVOICE_TITLE = "Подписка Makwin"

PAYMENT_THANKS_TEXT = "✅ Оплата прошла успешно! Готовим вашу подписку..."


def buy_subscription_text(price_stars: int, days: int) -> str:
    return (
        "💳 Покупка подписки Makwin\n\n"
        f"⭐ Telegram Stars — {price_stars} за {days} дней\n"
        "💳 Банковская карта — скоро доступно\n"
        "₿ Криптовалюта — скоро доступно\n\n"
        "Нажмите кнопку ниже, чтобы оплатить Stars 👇"
    )


def invoice_description_text(days: int) -> str:
    return f"Доступ к VPN на {days} дней. Оплата через Telegram Stars."

NO_ACTIVE_SUBSCRIPTION_TEXT = (
    "❌ У вас пока нет активной подписки.\n\n"
    "Нажмите 🚀 Получить VPN"
)

INSTRUCTION_TEXT = (
    "📖 Инструкция Makwin\n\n"
    "1️⃣ Установите клиент:\n"
    "• Android — Happ / v2rayNG\n"
    "• Windows — v2rayN\n"
    "• iOS — Streisand / Shadowrocket\n\n"
    "2️⃣ Нажмите 🚀 Получить VPN\n\n"
    "3️⃣ Добавьте ссылку подписки в приложение.\n\n"
    "VPN обновляется автоматически."
)

SUPPORT_TEXT = (
    "🆘 Поддержка Makwin\n\n"
    "Если возникли проблемы:\n"
    "• проверьте интернет\n"
    "• обновите подписку\n"
    "• перезапустите VPN клиент\n\n"
    "Связь с поддержкой:\n"
    "@ваш_username"
)


def subscription_issued_text(sub_url: str, expiry_str: str) -> str:
    return (
        "✅ Подписка выдана!\n\n"
        f"Действует до: {expiry_str}\n\n"
        f"Ссылка для добавления в клиент (v2rayN, Happ, Hiddify и т.д.):\n"
        f"`{sub_url}`\n\n"
        "Или отсканируйте QR-код ниже."
    )


def my_subscription_text(status: str, expiry_str: str, sub_url: str) -> str:
    return (
        "📱 Ваша подписка\n\n"
        f"Статус: {status}\n"
        f"До: {expiry_str}\n\n"
        f"Ссылка для добавления в клиент (v2rayN, Happ, Hiddify и т.д.):\n"
        f"`{sub_url}`\n\n"
        "Или отсканируйте QR-код выше."
    )