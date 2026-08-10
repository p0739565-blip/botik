import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Переменная окружения {name} не задана (см. .env)")
    return value.strip()


def _require_int(name: str) -> int:
    raw = _require(name)
    try:
        return int(raw)
    except ValueError:
        raise RuntimeError(
            f"Переменная окружения {name}={raw!r} должна быть целым числом (см. .env)"
        )


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw.strip())
    except ValueError:
        raise RuntimeError(
            f"Переменная окружения {name}={raw!r} должна быть целым числом (см. .env)"
        )


# Telegram
BOT_TOKEN = _require("BOT_TOKEN")
CHANNEL_ID = _require_int("CHANNEL_ID")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "").strip().lstrip("@")

# Подписка
SUB_DOMAIN = _require("SUB_DOMAIN").strip().rstrip("/")


# ==========================
# Локальная база SQLite
# ==========================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_FILE = DATA_DIR / "database.db"
DATABASE_URL = f"sqlite+aiosqlite:///{DB_FILE}"

SUPPORT_MEDIA_DIR = DATA_DIR / "support_media"
SUPPORT_MEDIA_DIR.mkdir(parents=True, exist_ok=True)

BROADCAST_MEDIA_DIR = DATA_DIR / "broadcast_media"
BROADCAST_MEDIA_DIR.mkdir(parents=True, exist_ok=True)

# ==========================
# Админ-панель
# ==========================

# Секрет для подписи сессионных cookie админки. Можно задать в .env
# (ADMIN_SESSION_SECRET=...) — тогда сессии переживут ЛЮБОЙ рестарт
# сервиса. Если не задан — генерируется один раз и сохраняется в файл
# рядом с базой, чтобы не разлогинивать всех при каждом перезапуске
# (но при переносе на новый сервер без переноса этого файла все
# сессии всё равно инвалидируются — это нормально и ожидаемо).
_admin_secret_env = os.getenv("ADMIN_SESSION_SECRET", "").strip()

if _admin_secret_env:
    ADMIN_SESSION_SECRET = _admin_secret_env
else:
    _secret_file = DATA_DIR / "admin_session.key"
    if _secret_file.exists():
        ADMIN_SESSION_SECRET = _secret_file.read_text().strip()
    else:
        import secrets as _secrets

        ADMIN_SESSION_SECRET = _secrets.token_hex(32)
        _secret_file.write_text(ADMIN_SESSION_SECRET)
