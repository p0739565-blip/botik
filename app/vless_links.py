"""Источник списка конфигов (vless/hy2), которые сервер отдаёт по
/sub/<token>. Раньше список был статичным списком в этом файле —
теперь он хранится в таблице vless_links и правится через админку
(/admin/vless-links), без правки кода и перезапуска процессов.

Старые захардкоженные списки (если нужно перенести их в БД разово)
лежат в app/vless_links_seed.py — см. инструкцию там.
"""

from sqlalchemy import select

from app.db import async_session
from app.models import VlessLink


async def render_links(uuid: str) -> list[str]:
    """Возвращает активные рабочие ссылки в заданном порядке.

    Аргумент uuid оставлен для обратной совместимости сигнатуры (раньше
    подставлялся в шаблон ссылки) — сейчас ссылки статичны и одинаковы
    для всех, как было и в старой версии, поэтому не используется.
    """
    async with async_session() as session:
        result = await session.execute(
            select(VlessLink.url)
            .where(VlessLink.is_dead.is_(False), VlessLink.is_active.is_(True))
            .order_by(VlessLink.position, VlessLink.id)
        )
        return list(result.scalars().all())


async def get_dead_links() -> list[str]:
    """Заглушечные ссылки, которые отдаются вместо обычного списка,
    если токен не найден или подписка истекла."""
    async with async_session() as session:
        result = await session.execute(
            select(VlessLink.url)
            .where(VlessLink.is_dead.is_(True), VlessLink.is_active.is_(True))
            .order_by(VlessLink.position, VlessLink.id)
        )
        return list(result.scalars().all())
