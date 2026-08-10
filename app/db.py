from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_models() -> None:
    """Создаёт таблицы, если их ещё нет. Для MVP вместо Alembic-миграций.

    Ленивые импорты здесь — намеренно: некоторые таблицы (например,
    support_messages) ссылаются через ForeignKey на таблицы админки
    (admin_users), а процесс бота (app/bot.py) никогда не импортирует
    app.admin.* напрямую. Без явной регистрации обеих групп моделей
    здесь create_all() упадёт с NoReferencedTableError именно в
    бот-процессе (в API-процессе всё работало бы и без этого, т.к.
    app.admin.router и так их импортирует)."""
    from app import models as _models  # noqa: F401
    from app.admin import models as _admin_models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
