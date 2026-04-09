from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Date, Integer, Boolean, DateTime, Text, ForeignKey, Enum
from datetime import date, datetime
from typing import Optional

class ReviewBase(Base):
	__tablename__ = "review"

	id: Mapped[int] = mapped_column(primary_key=True)
    deal_id: Mapped[int] = mapped_column(ForeignKey("deal.id"))
    client_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    lawyer_id: Mapped[int] = mapped_column(ForeignKey("lawyer_profile.id"))
    rating: Mapped[int] = mapped_column(Integer())
    text: Mapped[str] = mapped_column(String(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime())