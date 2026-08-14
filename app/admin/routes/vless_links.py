from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select

from app.admin.auth import require_permission, write_audit_log
from app.admin.models import AdminUser, Permission
from app.db import async_session
from app.models import VlessLink

router = APIRouter(prefix="/vless-links", tags=["vless-links"])


async def _next_position(session, is_dead: bool) -> int:
    result = await session.execute(
        select(VlessLink.position)
        .where(VlessLink.is_dead.is_(is_dead))
        .order_by(VlessLink.position.desc())
        .limit(1)
    )
    last = result.scalar_one_or_none()
    return (last + 1) if last is not None else 0


@router.get("")
async def list_links(
    request: Request,
    admin: AdminUser = Depends(require_permission(Permission.MANAGE_VLESS_LINKS)),
):
    from app.admin.router import templates

    async with async_session() as session:
        working = (
            await session.execute(
                select(VlessLink)
                .where(VlessLink.is_dead.is_(False))
                .order_by(VlessLink.position, VlessLink.id)
            )
        ).scalars().all()
        dead = (
            await session.execute(
                select(VlessLink)
                .where(VlessLink.is_dead.is_(True))
                .order_by(VlessLink.position, VlessLink.id)
            )
        ).scalars().all()

    return templates.TemplateResponse(
        "vless_links.html",
        {
            "request": request,
            "admin": admin,
            "working": working,
            "dead": dead,
            "working_active_count": sum(1 for link in working if link.is_active),
        },
    )


@router.get("/new")
async def new_link_form(
    request: Request,
    dead: int = 0,
    admin: AdminUser = Depends(require_permission(Permission.MANAGE_VLESS_LINKS)),
):
    from app.admin.router import templates

    return templates.TemplateResponse(
        "vless_link_form.html",
        {
            "request": request,
            "admin": admin,
            "link": None,
            "is_dead": bool(dead),
            "error": None,
        },
    )


@router.post("/new")
async def create_link(
    request: Request,
    url: str = Form(...),
    note: str = Form(""),
    is_dead: str = Form("0"),
    admin: AdminUser = Depends(require_permission(Permission.MANAGE_VLESS_LINKS)),
):
    from app.admin.router import templates

    url = url.strip()
    is_dead_bool = is_dead == "1"

    if not url.startswith(("vless://", "vmess://", "hy2://", "hysteria2://", "trojan://", "ss://")):
        return templates.TemplateResponse(
            "vless_link_form.html",
            {
                "request": request,
                "admin": admin,
                "link": None,
                "is_dead": is_dead_bool,
                "error": "Похоже, это не ссылка-конфиг (ожидается vless://, hy2:// и т.п.)",
            },
            status_code=400,
        )

    async with async_session() as session:
        position = await _next_position(session, is_dead_bool)
        link = VlessLink(
            url=url,
            note=note.strip() or None,
            is_dead=is_dead_bool,
            is_active=True,
            position=position,
        )
        session.add(link)
        await session.commit()
        link_id = link.id

    await write_audit_log(
        admin,
        action="create_vless_link",
        target=f"vless_link_id={link_id}",
        details=f"is_dead={is_dead_bool}",
    )

    return RedirectResponse("/admin/vless-links", status_code=303)


@router.get("/{link_id}/edit")
async def edit_link_form(
    request: Request,
    link_id: int,
    admin: AdminUser = Depends(require_permission(Permission.MANAGE_VLESS_LINKS)),
):
    from app.admin.router import templates

    async with async_session() as session:
        link = await session.get(VlessLink, link_id)

    if link is None:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")

    return templates.TemplateResponse(
        "vless_link_form.html",
        {
            "request": request,
            "admin": admin,
            "link": link,
            "is_dead": link.is_dead,
            "error": None,
        },
    )


@router.post("/{link_id}/edit")
async def edit_link(
    request: Request,
    link_id: int,
    url: str = Form(...),
    note: str = Form(""),
    admin: AdminUser = Depends(require_permission(Permission.MANAGE_VLESS_LINKS)),
):
    from app.admin.router import templates

    url = url.strip()

    if not url.startswith(("vless://", "vmess://", "hy2://", "hysteria2://", "trojan://", "ss://")):
        async with async_session() as session:
            link = await session.get(VlessLink, link_id)
        return templates.TemplateResponse(
            "vless_link_form.html",
            {
                "request": request,
                "admin": admin,
                "link": link,
                "is_dead": link.is_dead if link else False,
                "error": "Похоже, это не ссылка-конфиг (ожидается vless://, hy2:// и т.п.)",
            },
            status_code=400,
        )

    async with async_session() as session:
        link = await session.get(VlessLink, link_id)
        if link is None:
            raise HTTPException(status_code=404, detail="Ссылка не найдена")

        link.url = url
        link.note = note.strip() or None
        await session.commit()

    await write_audit_log(
        admin, action="edit_vless_link", target=f"vless_link_id={link_id}"
    )

    return RedirectResponse("/admin/vless-links", status_code=303)


@router.post("/{link_id}/toggle")
async def toggle_link(
    link_id: int,
    admin: AdminUser = Depends(require_permission(Permission.MANAGE_VLESS_LINKS)),
):
    async with async_session() as session:
        link = await session.get(VlessLink, link_id)
        if link is None:
            raise HTTPException(status_code=404, detail="Ссылка не найдена")

        link.is_active = not link.is_active
        new_status = link.is_active
        await session.commit()

    await write_audit_log(
        admin,
        action="toggle_vless_link",
        target=f"vless_link_id={link_id}",
        details=f"is_active={new_status}",
    )

    return RedirectResponse("/admin/vless-links", status_code=303)


@router.post("/{link_id}/delete")
async def delete_link(
    link_id: int,
    admin: AdminUser = Depends(require_permission(Permission.MANAGE_VLESS_LINKS)),
):
    async with async_session() as session:
        link = await session.get(VlessLink, link_id)
        if link is None:
            raise HTTPException(status_code=404, detail="Ссылка не найдена")

        await session.delete(link)
        await session.commit()

    await write_audit_log(
        admin, action="delete_vless_link", target=f"vless_link_id={link_id}"
    )

    return RedirectResponse("/admin/vless-links", status_code=303)


@router.post("/{link_id}/move")
async def move_link(
    link_id: int,
    direction: str = Form(...),
    admin: AdminUser = Depends(require_permission(Permission.MANAGE_VLESS_LINKS)),
):
    """Меняет местами позицию ссылки с соседней (в пределах своего же
    набора — рабочие и dead сортируются отдельно друг от друга)."""
    if direction not in ("up", "down"):
        raise HTTPException(status_code=400, detail="Неизвестное направление")

    async with async_session() as session:
        link = await session.get(VlessLink, link_id)
        if link is None:
            raise HTTPException(status_code=404, detail="Ссылка не найдена")

        siblings = (
            await session.execute(
                select(VlessLink)
                .where(VlessLink.is_dead.is_(link.is_dead))
                .order_by(VlessLink.position, VlessLink.id)
            )
        ).scalars().all()

        idx = next((i for i, s in enumerate(siblings) if s.id == link.id), None)
        if idx is None:
            raise HTTPException(status_code=404, detail="Ссылка не найдена")

        swap_idx = idx - 1 if direction == "up" else idx + 1
        if 0 <= swap_idx < len(siblings):
            other = siblings[swap_idx]
            link.position, other.position = other.position, link.position
            await session.commit()

    return RedirectResponse("/admin/vless-links", status_code=303)
