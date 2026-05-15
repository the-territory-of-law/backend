from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.orm_base import Base


class DisputeStatusType(str, Enum):
    OPEN = "open"
    RESOLVED = "resolved"


class DisputeResolutionStatusType(str, Enum):
    CLIENT_WIN = "client_win"
    LAWYER_WIN = "lawyer_win"
    DRAW = "draw"


class Dispute(Base):
    __tablename__ = "dispute"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    deal_id: Mapped[int] = mapped_column(ForeignKey("deal.id"))
    opened_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[DisputeStatusType] = mapped_column(
        SAEnum(DisputeStatusType, name="dispute_status", native_enum=False),
        default=DisputeStatusType.OPEN,
    )
    reason: Mapped[str] = mapped_column(String())
    resolution: Mapped[DisputeResolutionStatusType] = mapped_column(
        SAEnum(DisputeResolutionStatusType, name="dispute_resolution_status", native_enum=False),
        default=DisputeResolutionStatusType.DRAW,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
