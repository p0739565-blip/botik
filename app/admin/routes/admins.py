from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.admin.auth import get_admin_by_id, hash_password, write_audit_log
from app.admin.auth import require_permission
from app.admin.models import (
    ROLE_DEFAULT_PERMISSIONS,
    AdminPermission,
    AdminRole,
    AdminUser,
    Permission,
)
from app.db import async_session

router = APIRouter(prefix="/admins", tags=["admins"])


@router.get("")
async def admins_list(
    request: Request,
    admin: AdminUser = Depends(require_permission(Permission.MANAGE_ADMINS)),
):
    from app.admin.router import templates

    async with async_session() as session:
        result = await session.execute(
            select(AdminUser)
            .options(selectinload(AdminUser.permissions))
            .order_by(AdminUser.created_at)
        )
        admins = result.scalars().all()

    return templates.TemplateResponse(
        "admins.html",
        {"request": request, "admin": admin, "admins": admins},
    )


@router.get("/new")
async def new_admin_form(
    request: Request,
    admin: AdminUser = Depends(require_permission(Permission.MANAGE_ADMINS)),
):
    from app.admin.router import templates

    return templates.TemplateResponse(
        "admin_form.html",
        {
            "request": request,
            "admin": admin,
            "target": None,
            "all_permissions": list(Permission),
            "roles": list(AdminRole),
            "error": None,
        },
    )


@router.post("/new")
async def create_admin(
    request: Request,
    login: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    admin: AdminUser = Depends(require_permission(Permission.MANAGE_ADMINS)),
):
    from app.admin.router import templates

    login = login.strip()

    if len(login) < 3 or len(password) < 8:
        return templates.TemplateResponse(
            "admin_form.html",
            {
                "request": request,
                "admin": admin,
                "target": None,
                "all_permissions": list(Permission),
                "roles": list(AdminRole),
                "error": "Логин от 3 символов, пароль от 8 символов",
            },
            status_code=400,
        )

    try:
        role_enum = AdminRole(role)
    except ValueError:
        raise HTTPException(status_code=400, detail="Неизвестная роль")

    form = await request.form()
    selected_permissions = form.getlist("permissions")

    async with async_session() as session:
        existing = await session.execute(
            select(AdminUser).where(AdminUser.login == login)
        )
        if existing.scalar_one_or_none() is not None:
            return templates.TemplateResponse(
                "admin_form.html",
                {
                    "request": request,
                    "admin": admin,
                    "target": None,
                    "all_permissions": list(Permission),
                    "roles": list(AdminRole),
                    "error": "Такой логин уже занят",
                },
                status_code=400,
            )

        new_admin = AdminUser(
            login=login,
            password_hash=hash_password(password),
            role=role_enum,
        )
        session.add(new_admin)
        await session.flush()  # получить new_admin.id до коммита

        perms = selected_permissions or [
            p.value for p in ROLE_DEFAULT_PERMISSIONS[role_enum]
        ]
        for perm_value in perms:
            session.add(
                AdminPermission(admin_id=new_admin.id, permission=Permission(perm_value))
            )

        await session.commit()
        new_admin_id = new_admin.id

    await write_audit_log(
        admin,
        action="create_admin",
        target=f"login={login}",
        details=f"role={role_enum.value}",
    )

    return RedirectResponse(f"/admin/admins/{new_admin_id}/edit", status_code=303)


@router.get("/{admin_id}/edit")
async def edit_admin_form(
    request: Request,
    admin_id: int,
    admin: AdminUser = Depends(require_permission(Permission.MANAGE_ADMINS)),
):
    from app.admin.router import templates

    target = await get_admin_by_id(admin_id)
    if target is None:
        raise HTTPException(status_code=404, detail="Админ не найден")

    return templates.TemplateResponse(
        "admin_form.html",
        {
            "request": request,
            "admin": admin,
            "target": target,
            "target_permissions": {p.permission for p in target.permissions},
            "all_permissions": list(Permission),
            "roles": list(AdminRole),
            "error": None,
        },
    )


@router.post("/{admin_id}/edit")
async def edit_admin(
    request: Request,
    admin_id: int,
    role: str = Form(...),
    new_password: str = Form(""),
    admin: AdminUser = Depends(require_permission(Permission.MANAGE_ADMINS)),
):
    try:
        role_enum = AdminRole(role)
    except ValueError:
        raise HTTPException(status_code=400, detail="Неизвестная роль")

    form = await request.form()
    selected_permissions = form.getlist("permissions")

    async with async_session() as session:
        result = await session.execute(
            select(AdminUser)
            .options(selectinload(AdminUser.permissions))
            .where(AdminUser.id == admin_id)
        )
        target = result.scalar_one_or_none()

        if target is None:
            raise HTTPException(status_code=404, detail="Админ не найден")

        target.role = role_enum

        if new_password.strip():
            if len(new_password.strip()) < 8:
                raise HTTPException(
                    status_code=400, detail="Пароль от 8 символов"
                )
            target.password_hash = hash_password(new_password.strip())

        # Полностью пересобираем набор прав под выбранные галочки.
        for existing_perm in list(target.permissions):
            await session.delete(existing_perm)

        for perm_value in selected_permissions:
            session.add(
                AdminPermission(admin_id=admin_id, permission=Permission(perm_value))
            )

        await session.commit()

    await write_audit_log(
        admin,
        action="edit_admin",
        target=f"admin_id={admin_id}",
        details=f"role={role_enum.value}, permissions={selected_permissions}",
    )

    return RedirectResponse("/admin/admins", status_code=303)


@router.post("/{admin_id}/deactivate")
async def deactivate_admin(
    admin_id: int,
    admin: AdminUser = Depends(require_permission(Permission.MANAGE_ADMINS)),
):
    if admin_id == admin.id:
        raise HTTPException(
            status_code=400, detail="Нельзя деактивировать самого себя"
        )

    async with async_session() as session:
        result = await session.execute(
            select(AdminUser).where(AdminUser.id == admin_id)
        )
        target = result.scalar_one_or_none()

        if target is None:
            raise HTTPException(status_code=404, detail="Админ не найден")

        target.is_active = not target.is_active
        new_status = target.is_active

        await session.commit()

    await write_audit_log(
        admin,
        action="toggle_admin_active",
        target=f"admin_id={admin_id}",
        details=f"is_active={new_status}",
    )

    return RedirectResponse("/admin/admins", status_code=303)
