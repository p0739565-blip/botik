import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Персональный uuid для xray/reality — один на аккаунт, не меняется
    # между продлениями подписки. Именно по нему сервер отличает
    # пользователей друг от друга и считает устройства.
    vless_uuid: Mapped[str] = mapped_column(String(36), unique=True, index=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(),
        default=datetime.datetime.now,
    )

    subscriptions: Mapped[list["Subscription"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    devices: Mapped[list["Device"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)

    expiry: Mapped[datetime.datetime] = mapped_column(DateTime())

    # Лимит устройств для этого тарифа (2-10, задаётся при покупке)
    device_limit: Mapped[int] = mapped_column(Integer, default=3)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(),
        default=datetime.datetime.now,
    )

    user: Mapped["User"] = relationship(back_populates="subscriptions")

    @property
    def is_valid(self) -> bool:
        """Проверка активности подписки."""
        return self.is_active and self.expiry > datetime.datetime.now()


class Device(Base):
    """Устройство, замеченное сервером по IP-адресу подключения с данным
    uuid. Это приближённый счётчик — см. пояснение в README про точность
    подсчёта по IP."""

    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    ip: Mapped[str] = mapped_column(String(45), index=True)  # хватает и на IPv6

    first_seen: Mapped[datetime.datetime] = mapped_column(
        DateTime(), default=datetime.datetime.now
    )
    last_seen: Mapped[datetime.datetime] = mapped_column(
        DateTime(), default=datetime.datetime.now
    )
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(back_populates="devices")


class Payment(Base):
    """История успешных оплат — для админки (раздел «Платежи») и
    статистики на дашборде. Пишется в момент successful_payment,
    отдельно от Subscription: подписка может быть продлена, а платёж —
    это просто зафиксированный факт транзакции."""

    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    tariff_key: Mapped[str] = mapped_column(String(32))
    method: Mapped[str] = mapped_column(String(16))  # "stars" | "card" | "crypto"
    amount: Mapped[int] = mapped_column(Integer)  # в минимальных единицах метода
    days: Mapped[int] = mapped_column(Integer)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(), default=datetime.datetime.now
    )

    user: Mapped["User"] = relationship()
