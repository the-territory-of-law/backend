from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, DateTime, Text, ForeignKey
from datetime import datetime
from typing import Optional
from sqlalchemy import Enum as SAEnum

from app.modules.users.schemas import UserRole


class Base(DeclarativeBase):
	pass

class User(Base):
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(primary_key=True)
	username: Mapped[str] = mapped_column(String())
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role"),
        default=UserRole.CLIENT,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime())
    hashed_password: Mapped[str] = mapped_column(String())
    email: Mapped[str] = mapped_column(String(), unique=True)


