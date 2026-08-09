import datetime
import enum

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class AdminRole(str, enum.Enum):
    """Пресет прав, применяемый одним кликом при создании админа.
    Реальная проверка прав всегда идёт через Permission/AdminPermission,
    роль — это только удобный ярлык + значение по умолчанию для UI."""

    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    OBSERVER = "observer"


class Permission(str, enum.Enum):
    """Полный справочник прав в системе. Хранится как строка в БД
    (через AdminPermission), а не как отдельная таблица-справочник —
    добавление нового права не требует миграции данных, только новое
    значение enum."""

    # Просмотр (доступно даже наблюдателю)
    VIEW_DASHBOARD = "view_dashboard"
    VIEW_USERS = "view_users"
    VIEW_SUBSCRIPTIONS = "view_subscriptions"
    VIEW_PAYMENTS = "view_payments"

    # Управление пользователями/подписками (базовый админ)
    ISSUE_SUBSCRIPTION = "issue_subscription"      # ручная выдача/продление
    REVOKE_SUBSCRIPTION = "revoke_subscription"     # ручной отзыв/активация

    # Очистка старой истории подписок (удаление старых неактивных
    # записей из БД) — отдельное право, т.к. действие необратимое
    PURGE_SUBSCRIPTIONS = "purge_subscriptions"

    # Тарифы и рассылки (обычно только супер-админ, но право отдельное —
    # можно выдать и обычному админу точечно)
    MANAGE_TARIFFS = "manage_tariffs"
    BROADCAST_MESSAGE = "broadcast_message"

    # Только супер-админ
    MANAGE_ADMINS = "manage_admins"
    VIEW_AUDIT_LOG = "view_audit_log"
    MANAGE_SERVER_SETTINGS = "manage_server_settings"  # задел на будущее


# Пресеты: какие права получает админ при выборе роли в UI.
# Дальше супер-админ может донастроить вручную — это только стартовый набор.
ROLE_DEFAULT_PERMISSIONS: dict[AdminRole, set[Permission]] = {
    AdminRole.OBSERVER: {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_USERS,
        Permission.VIEW_SUBSCRIPTIONS,
        Permission.VIEW_PAYMENTS,
    },
    AdminRole.ADMIN: {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_USERS,
        Permission.VIEW_SUBSCRIPTIONS,
        Permission.VIEW_PAYMENTS,
        Permission.ISSUE_SUBSCRIPTION,
        Permission.REVOKE_SUBSCRIPTION,
    },
    AdminRole.SUPER_ADMIN: set(Permission),  # вообще все права
}


class AdminUser(Base):
    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(primary_key=True)

    login: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))

    role: Mapped[AdminRole] = mapped_column(Enum(AdminRole))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # Деактивация вместо удаления — чтобы не терять audit log по этому
    # админу (FK на удалённую строку сломает историю действий).

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(), default=datetime.datetime.now
    )
    last_login_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(), nullable=True
    )

    permissions: Mapped[list["AdminPermission"]] = relationship(
        back_populates="admin",
        cascade="all, delete-orphan",
    )

    def has_permission(self, permission: Permission) -> bool:
        if not self.is_active:
            return False
        return any(p.permission == permission for p in self.permissions)


class AdminPermission(Base):
    """Конкретное право, выданное конкретному админу.
    many-to-many между AdminUser и Permission, но через явную таблицу
    (а не association table) — чтобы потом можно было добавить, например,
    granted_by/granted_at без миграции структуры."""

    __tablename__ = "admin_permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    admin_id: Mapped[int] = mapped_column(ForeignKey("admin_users.id"), index=True)

    permission: Mapped[Permission] = mapped_column(Enum(Permission))

    admin: Mapped["AdminUser"] = relationship(back_populates="permissions")


class AuditLog(Base):
    """Журнал действий админов. Пишется на каждое изменяющее действие
    (не на просмотр — иначе таблица разрастётся без пользы)."""

    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    admin_id: Mapped[int] = mapped_column(ForeignKey("admin_users.id"), index=True)

    action: Mapped[str] = mapped_column(String(64))
    # например: "issue_subscription", "delete_user", "create_admin"

    target: Mapped[str | None] = mapped_column(String(128), nullable=True)
    # что именно изменили, например "user_id=123" или "admin login=ivan"

    details: Mapped[str | None] = mapped_column(Text(), nullable=True)
    # произвольный JSON/текст с деталями (было/стало), если нужно

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(), default=datetime.datetime.now
    )

    admin: Mapped["AdminUser"] = relationship()