"""ORM-модели чата: сообщения, вложения, статусы доставки, история правок текста."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.orm_base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ChatAttachmentKind(str, PyEnum):
    IMAGE = "image"
    FILE = "file"


class ChatDeliveryStatus(str, PyEnum):
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class ChatMessage(Base):
    """Сообщение в чате сделки (контейнер: текст + вложения)."""

    __tablename__ = "chat_message"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    deal_id: Mapped[int] = mapped_column(ForeignKey("deal.id", ondelete="CASCADE"), index=True)
    # Клиент по сделке (денормализация для API; заполняется при создании сообщения)
    client_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    text: Mapped[str | None] = mapped_column(Text(), nullable=True)
    blocked_reason: Mapped[str | None] = mapped_column(String(512), nullable=True)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    edited_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    attachments: Mapped[list[ChatAttachment]] = relationship(
        back_populates="message",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="ChatAttachment.id",
    )
    delivery_statuses: Mapped[list[ChatMessageDeliveryStatus]] = relationship(
        back_populates="message",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="ChatMessageDeliveryStatus.at",
    )
    edit_history: Mapped[list[ChatMessageEditHistory]] = relationship(
        back_populates="message",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="ChatMessageEditHistory.edited_at",
    )


class ChatAttachment(Base):
    """Вложение к сообщению (файл или изображение).

    До привязки к сообщению: ``message_id`` NULL, заполнены ``deal_id`` и
    ``uploaded_by_id`` (предзагрузка для WebSocket / ``attachment_ids``).
    """

    __tablename__ = "chat_attachment"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    message_id: Mapped[int | None] = mapped_column(
        ForeignKey("chat_message.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    deal_id: Mapped[int | None] = mapped_column(
        ForeignKey("deal.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    uploaded_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    kind: Mapped[ChatAttachmentKind] = mapped_column(
        SAEnum(ChatAttachmentKind, name="chat_attachment_kind", native_enum=False),
    )
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    size: Mapped[int] = mapped_column(BigInteger(), nullable=False, default=0)
    mime: Mapped[str] = mapped_column(String(255), nullable=False)
    width: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    height: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    message: Mapped[ChatMessage | None] = relationship(back_populates="attachments")


class ChatMessageDeliveryStatus(Base):
    """Статус доставки/прочтения для участника (по одному ряду на пару message + user)."""

    __tablename__ = "chat_message_delivery_status"
    __table_args__ = (
        UniqueConstraint("message_id", "user_id", name="uq_chat_message_delivery_message_user"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    message_id: Mapped[int] = mapped_column(
        ForeignKey("chat_message.id", ondelete="CASCADE"),
        index=True,
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    status: Mapped[ChatDeliveryStatus] = mapped_column(
        SAEnum(ChatDeliveryStatus, name="chat_delivery_status", native_enum=False),
    )
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    message: Mapped[ChatMessage] = relationship(back_populates="delivery_statuses")


class ChatMessageEditHistory(Base):
    """История изменения текстовой части сообщения."""

    __tablename__ = "chat_message_edit_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    message_id: Mapped[int] = mapped_column(
        ForeignKey("chat_message.id", ondelete="CASCADE"),
        index=True,
    )
    old_text: Mapped[str | None] = mapped_column(Text(), nullable=True)
    edited_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    message: Mapped[ChatMessage] = relationship(back_populates="edit_history")
