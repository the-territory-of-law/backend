from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Date, Integer, Boolean, DateTime, Text, ForeignKey, Enum
from datetime import date, datetime
from typing import Optional

class DisputeStatusType(str, PyEnum):
    OPEN = "open"
    RESOLVED = "resolved"

class DisputeResolutionStatusType(str, PyEnum):
    CLIENT_WIN = "client_win"
    LAWYER_WIN = "lawyer_win"
    DRAW = "draw"

class DisputeBase(Base):
	__tablename__ = "dispute"

	id: Mapped[int] = mapped_column(primary_key=True)
    deal_id: Mapped[int] = mapped_column(ForeignKey("deal.id"))
    opened_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[DisputeStatusType] = mapped_column(
        Enum(DisputeStatusType, name="dispute_status"),
        default=DisputeStatusType.OPEN
    )
    reason: Mapped[str] = mapped_column(String())
    resolution: Mapped[DisputeResolutionStatusType] = mapped_column(
        Enum(DisputeResolutionStatusType, name="dispute_resolution_status"),
        default=DisputeResolutionStatusType.DRAW
    )
    created_at: Mapped[datetime] = mapped_column(DateTime())