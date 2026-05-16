from enum import Enum

from sqlalchemy import Enum as SAEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.orm_base import Base


class VerificationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class LawyerProfile(Base):
    __tablename__ = "lawyer_profile"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    city: Mapped[str | None] = mapped_column(String(), nullable=True)
    about: Mapped[str | None] = mapped_column(Text(), nullable=True)
    experience_years: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    verification_status: Mapped[VerificationStatus] = mapped_column(
        SAEnum(VerificationStatus, name="verification_status", native_enum=False),
        default=VerificationStatus.PENDING,
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))


class PracticeArea(Base):
    __tablename__ = "practice_area"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String())


class LawyerPracticeArea(Base):
    __tablename__ = "lawyer_practice_area"

    lawyer_id: Mapped[int] = mapped_column(ForeignKey("lawyer_profile.id"), primary_key=True)
    practice_area_id: Mapped[int] = mapped_column(ForeignKey("practice_area.id"), primary_key=True)
