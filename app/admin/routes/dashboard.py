import datetime

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select

from app.admin.auth import require_permission
from app.admin.models import AdminUser, Permission
from app.db import async_session
from app.models import Payment, Subscription, User

router = APIRouter(tags=["dashboard"])


@router.get("/")
async def dashboard(
    request: Request,
    admin: AdminUser = Depends(require_permission(Permission.VIEW_DASHBOARD)),
):
    from app.admin.router import templates

    now = datetime.datetime.now()
    today_start = datetime.datetime(now.year, now.month, now.day)
    week_start = today_start - datetime.timedelta(days=7)

    async with async_session() as session:
        total_users = (
            await session.execute(select(func.count(User.id)))
        ).scalar_one()

        active_subs = (
            await session.execute(
                select(func.count(Subscription.id)).where(
                    Subscription.is_active == True,  # noqa: E712
                    Subscription.expiry > now,
                )
            )
        ).scalar_one()

        subs_today = (
            await session.execute(
                select(func.count(Subscription.id)).where(
                    Subscription.created_at >= today_start,
                )
            )
        ).scalar_one()

        subs_week = (
            await session.execute(
                select(func.count(Subscription.id)).where(
                    Subscription.created_at >= week_start,
                )
            )
        ).scalar_one()

        stars_today = (
            await session.execute(
                select(func.coalesce(func.sum(Payment.amount), 0)).where(
                    Payment.method == "stars",
                    Payment.created_at >= today_start,
                )
            )
        ).scalar_one()

        stars_total = (
            await session.execute(
                select(func.coalesce(func.sum(Payment.amount), 0)).where(
                    Payment.method == "stars",
                )
            )
        ).scalar_one()

        payments_total = (
            await session.execute(select(func.count(Payment.id)))
        ).scalar_one()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "admin": admin,
            "stats": {
                "total_users": total_users,
                "active_subs": active_subs,
                "subs_today": subs_today,
                "subs_week": subs_week,
                "stars_today": stars_today,
                "stars_total": stars_total,
                "payments_total": payments_total,
            },
        },
    )
