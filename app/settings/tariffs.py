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
        "days": 3,
        "stars": 0,
        "card": None,
        "crypto": None,
        "is_trial": True,
    },

    "1m": {
        "title": "📅1 месяц",
        "days": 30,
        "stars": 50,
        "card": 50,
        "crypto": None,
    },

    "3m": {
        "title": "📅3 месяца",
        "days": 90,
        "stars": 135,
        "card": 135,
        "crypto": None,
    },

    "6m": {
        "title": "📅6 месяцев",
        "days": 180,
        "stars": 240,
        "card": 240,
        "crypto": None,
    },

    "12m": {
        "title": "📅12 месяцев",
        "days": 365,
        "stars": 360,
        "card": 360,
        "crypto": None,
    },
}