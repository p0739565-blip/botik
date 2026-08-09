"""
Единый список тарифов.

Каждый тариф содержит:
- title      — название для пользователя
- days       — срок действия подписки
- stars      — стоимость в Telegram Stars
- card       — стоимость при оплате картой (будет использоваться позже)
- crypto     — стоимость в криптовалюте (будет использоваться позже)
- is_trial   — является ли тариф пробным
"""

TARIFFS = {
    "trial": {
        "title": "🎁 Пробный период",
        "days": 7,
        "stars": 0,
        "card": None,
        "crypto": None,
        "is_trial": True,
    },

    "1m": {
        "title": "📅 1 месяц",
        "days": 30,
        "stars": 50,
        "card": None,
        "crypto": None,
    },

    "3m": {
        "title": "📅 3 месяца",
        "days": 90,
        "stars": 390,
        "card": None,
        "crypto": None,
    },

    "6m": {
        "title": "📅 6 месяцев",
        "days": 180,
        "stars": 690,
        "card": None,
        "crypto": None,
    },

    "12m": {
        "title": "👑 12 месяцев",
        "days": 365,
        "stars": 1190,
        "card": None,
        "crypto": None,
    },
}