from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Date, Integer, Boolean, DateTime, Text, ForeignKey, Enum
from datetime import date, datetime
from typing import Optional

class ChatMassageBase(Base):
	__tablename__ = "chat_message"

	id: Mapped[int] = mapped_column(primary_key=True)
    deal_id: Mapped[int] = mapped_column(ForeignKey("deal.id"))
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    text: Mapped[str] = mapped_column(String())
    blocked_reason: Mapped[str] = mapped_column(String(), nullable=True)
    sent_at: Mapped[datetime] = mapped_column(DateTime())