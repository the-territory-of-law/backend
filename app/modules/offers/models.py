from datetime import date
from enum import Enum

from sqlalchemy import Date, Enum as SAEnum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.orm_base import Base


class OfferStatusType(str, Enum):
    REJECTED = "rejected"
    ACCEPTED = "accepted"
    PENDING = "pending"


class LawyerOffer(Base):
    __tablename__ = "lawyer_offer"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("user_request.id"))
    lawyer_id: Mapped[int] = mapped_column(ForeignKey("lawyer_profile.id"))
    status: Mapped[OfferStatusType] = mapped_column(
        SAEnum(OfferStatusType, name="offer_status", native_enum=False),
        default=OfferStatusType.PENDING,
    )
    what_included: Mapped[str] = mapped_column(String())
    price: Mapped[int] = mapped_column(Integer())
    term: Mapped[date] = mapped_column(Date())
