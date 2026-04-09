from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Date, Integer, Boolean, DateTime, Text, ForeignKey, Enum
from datetime import date, datetime
from typing import Optional

class Base(DeclarativeBase):
	pass


class DealStatusType(str, PyEnum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DealBase(Base):
	__tablename__ = "deal"

	id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("user_request.id"))
    offer_id: Mapped[int] = mapped_column(ForeignKey("lawyer_offer.id"))
    status: Mapped[DealStatusType] = mapped_column(
        Enum(DealStatusType, name="deal_status"),
        default=DealStatusType.IN_PROGRESS
    )
    amount: Mapped[int] = mapped_column(Integer())
    platform_fee: Mapped[int] = mapped_column(Integer())
    lawyer_amount: Mapped[int] = mapped_column(Integer())
    paid_at: Mapped[datetime] = mapped_column(DateTime())