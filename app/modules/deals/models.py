from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.orm_base import Base


class DealStatusType(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Deal(Base):
    __tablename__ = "deal"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("user_request.id"))
    offer_id: Mapped[int] = mapped_column(ForeignKey("lawyer_offer.id"))
    status: Mapped[DealStatusType] = mapped_column(
        SAEnum(DealStatusType, name="deal_status", native_enum=False),
        default=DealStatusType.IN_PROGRESS,
    )
    amount: Mapped[int] = mapped_column(Integer())
    platform_fee: Mapped[int] = mapped_column(Integer())
    lawyer_amount: Mapped[int] = mapped_column(Integer())
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
