import datetime

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import String, delete, select
from sqlalchemy.orm import selectinload

from app.admin.auth import require_permission, write_audit_log
from app.admin.models import AdminUser, Permission
from app.db import async_session
from app.models import Payment, Subscription, User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
async def users_list(
    request: Request,
    q: str = "",
    purged: int | None = None,
    admin: AdminUser = Depends(require_permission(Permission.VIEW_USERS)),
):
    from app.admin.router import templates

    async with async_session() as session:
        stmt = select(User).options(selectinload(User.subscriptions))

        if q.strip():
            needle = f"%{q.strip()}%"
            stmt = stmt.where(
                (User.username.ilike(needle)) | (User.tg_id.cast(String).ilike(needle))
            )

        stmt = stmt.order_by(User.created_at.desc()).limit(200)

        result = await session.execute(stmt)
        users = result.scalars().unique().all()

    rows = []
    now = datetime.datetime.now()
    for user in users:
        active_sub = next(
            (s for s in user.subscriptions if s.is_active and s.expiry > now),
            None,
        )
        rows.append({"user": user, "active_sub": active_sub})

    return templates.TemplateResponse(
        "users.html",
        {
            "request": request,
            "admin": admin,
            "rows": rows,
            "q": q,
            "purged": purged,
            "can_purge": admin.has_permission(Permission.PURGE_SUBSCRIPTIONS),
        },
    )


@router.get("/{user_id}")
async def user_detail(
    request: Request,
    user_id: int,
    purged: int | None = None,
    admin: AdminUser = Depends(require_permission(Permission.VIEW_USERS)),
):
    from app.admin.router import templates

    async with async_session() as session:
        result = await session.execute(
            select(User)
            .options(selectinload(User.subscriptions))
            .where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        payments_result = await session.execute(
            select(Payment)
            .where(Payment.user_id == user_id)
            .order_by(Payment.created_at.desc())
        )
        payments = payments_result.scalars().all()

    subs_sorted = sorted(
        user.subscriptions, key=lambda s: s.created_at, reverse=True
    )

    now = datetime.datetime.now()

    # "Активировать" имеет смысл только если есть отозванная подписка,
    # у которой срок ещё не истёк естественным образом — иначе это была
    # бы уже не активация, а фактически новая выдача (для этого есть
    # отдельная форма продления).
    can_activate = any(
        (not s.is_active) and s.expiry > now for s in subs_sorted
    )

    return templates.TemplateResponse(
        "user_detail.html",
        {
            "request": request,
            "admin": admin,
            "user": user,
            "subscriptions": subs_sorted,
            "payments": payments,
            "can_issue": admin.has_permission(Permission.ISSUE_SUBSCRIPTION),
            "can_revoke": admin.has_permission(Permission.REVOKE_SUBSCRIPTION),
            "can_activate": can_activate,
            "can_purge": admin.has_permission(Permission.PURGE_SUBSCRIPTIONS),
            "purged": purged,
        },
    )


@router.post("/{user_id}/extend")
async def extend_subscription(
    user_id: int,
    days: int = Form(...),
    admin: AdminUser = Depends(require_permission(Permission.ISSUE_SUBSCRIPTION)),
):
    if days <= 0 or days > 3650:
        raise HTTPException(status_code=400, detail="Некорректное число дней")

    # Переиспользуем ту же бизнес-логику продления, что и в боте —
    # чтобы поведение "продлить вручную из админки" не отличалось
    # от поведения "продлить через оплату".
    from app.services.subscription import issue_subscription

    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    await issue_subscription(user=user, days=days)

    await write_audit_log(
        admin,
        action="extend_subscription",
        target=f"user_id={user_id}",
        details=f"+{days} дней",
    )

    return RedirectResponse(f"/admin/users/{user_id}", status_code=303)


@router.post("/{user_id}/revoke")
async def revoke_subscription(
    user_id: int,
    admin: AdminUser = Depends(require_permission(Permission.REVOKE_SUBSCRIPTION)),
):
    """Отзыв — ссылка подписки сразу перестаёт отдавать рабочие сервера
    (см. /sub/{token} в api.py: неактивная подписка = мёртвые ссылки),
    независимо от того, что до истечения оригинального срока могло
    оставаться много времени. Сам срок (expiry) при этом не трогаем —
    это и позволяет потом "Активировать" обратно."""

    async with async_session() as session:
        result = await session.execute(
            select(Subscription)
            .where(
                Subscription.user_id == user_id,
                Subscription.is_active == True,  # noqa: E712
            )
            .order_by(Subscription.created_at.desc())
        )
        subscription = result.scalars().first()

        if subscription is not None:
            subscription.is_active = False
            await session.commit()

    await write_audit_log(
        admin,
        action="revoke_subscription",
        target=f"user_id={user_id}",
    )

    return RedirectResponse(f"/admin/users/{user_id}", status_code=303)


@router.post("/{user_id}/activate")
async def activate_subscription(
    user_id: int,
    admin: AdminUser = Depends(require_permission(Permission.REVOKE_SUBSCRIPTION)),
):
    """Обратное действие к "Отозвать": возвращает is_active=True самой
    свежей отозванной подписке — но только если у неё ещё не наступил
    исходный срок истечения. Если срок уже прошёл естественным образом —
    активировать нечего, нужно продлевать (форма "Продлить")."""

    now = datetime.datetime.now()

    async with async_session() as session:
        result = await session.execute(
            select(Subscription)
            .where(
                Subscription.user_id == user_id,
                Subscription.is_active == False,  # noqa: E712
                Subscription.expiry > now,
            )
            .order_by(Subscription.created_at.desc())
        )
        subscription = result.scalars().first()

        if subscription is not None:
            subscription.is_active = True
            await session.commit()

    await write_audit_log(
        admin,
        action="activate_subscription",
        target=f"user_id={user_id}",
    )

    return RedirectResponse(f"/admin/users/{user_id}", status_code=303)


async def _purge_old_subscriptions(days: int, user_id: int | None) -> int:
    """Удаляет из БД записи Subscription старше `days` дней (по дате
    покупки/выдачи), но ТОЛЬКО те, что уже неактуальны на текущий
    момент (is_active=False ИЛИ срок истёк) — действующие подписки,
    даже старые, никогда не трогаем. Если user_id передан — чистит
    только этого пользователя, иначе — по всей базе."""

    if days < 1:
        raise HTTPException(status_code=400, detail="Некорректный период")

    cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
    now = datetime.datetime.now()

    stmt = delete(Subscription).where(
        Subscription.created_at < cutoff,
        (Subscription.is_active == False) | (Subscription.expiry <= now),  # noqa: E712
    )

    if user_id is not None:
        stmt = stmt.where(Subscription.user_id == user_id)

    async with async_session() as session:
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount or 0


@router.post("/purge")
async def purge_subscriptions_global(
    days: int = Form(365),
    admin: AdminUser = Depends(require_permission(Permission.PURGE_SUBSCRIPTIONS)),
):
    count = await _purge_old_subscriptions(days=days, user_id=None)

    await write_audit_log(
        admin,
        action="purge_subscriptions",
        target="all_users",
        details=f"older than {days} days, deleted={count}",
    )

    return RedirectResponse(f"/admin/users?purged={count}", status_code=303)


@router.post("/{user_id}/purge")
async def purge_subscriptions_user(
    user_id: int,
    days: int = Form(365),
    admin: AdminUser = Depends(require_permission(Permission.PURGE_SUBSCRIPTIONS)),
):
    count = await _purge_old_subscriptions(days=days, user_id=user_id)

    await write_audit_log(
        admin,
        action="purge_subscriptions",
        target=f"user_id={user_id}",
        details=f"older than {days} days, deleted={count}",
    )

    return RedirectResponse(f"/admin/users/{user_id}?purged={count}", status_code=303)