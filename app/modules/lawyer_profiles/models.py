from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, DateTime, Text, ForeignKey, Enum
from datetime import datetime
from typing import Optional

class Base(DeclarativeBase):
	pass

class VerificationStatus(str, PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class LawyerProfileBase(Base):
	__tablename__ = "lawyer_profile"

	id: Mapped[int] = mapped_column(primary_key=True)
	city: Mapped[str] = mapped_column(String(), nullable=True)
    about: Mapped[str] = mapped_column(String(), nullable=True)
    experience_years: Mapped[int] = mapped_column(Integer(), nullable=True)
    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus, name="verification_status"),
        default=VerificationStatus.PENDING
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

class PracticeAreaBase(Base):
	__tablename__ = "practice_area"

	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str] = mapped_column(String())

class LawyerPracticeAreaBase(Base):
	__tablename__ = "lawyer_practice_area"

	lawyer_id: Mapped[int] = mapped_column(ForeignKey("lawyer_profile.id"))
	practice_area_id: Mapped[int] = mapped_column(ForeignKey("practice_area.id"))
    