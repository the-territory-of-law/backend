from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, DateTime, Text, ForeignKey
from datetime import datetime
from typing import Optional

class Base(DeclarativeBase):
	pass

class UserBase(Base):
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(primary_key=True)
	username: Mapped[str] = mapped_column(String())
    role: Mapped[str] = mapped_column(String())
    created_at: Mapped[datetime] = mapped_column(DateTime())
    hashed_password: Mapped[str] = mapped_column(String())
    email: Mapped[str] = mapped_column(String(), unique=True)


