from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Date, Integer, Boolean, DateTime, Text, ForeignKey, Enum
from datetime import datetime, date
from typing import Optional
class Base(DeclarativeBase):
	pass

class OfferStatusType(str, PyEnum):
    REJECTED = "rejected"
    ACCEPTED = "accepted"
    PENDING = "pending"


class LawyerOfferBase(Base):
	__tablename__ = "lawyer_offer"

	id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("user_request.id"))
    lawyer_id: Mapped[int] = mapped_column(ForeignKey("lawyer_profile.id"))
    status: Mapped[OfferStatusType] = mapped_column(
        Enum(OfferStatusType, name="offer_status"),
        default=OfferStatusType.PENDING
    )
    what_included: Mapped[str] = mapped_column(String())
    price: Mapped[int] = mapped_column(Integer())
    term: Mapped[date] = mapped_column(Date())