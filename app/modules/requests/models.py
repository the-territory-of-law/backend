from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, DateTime, Text, ForeignKey, Enum
from datetime import datetime
from typing import Optional

class Base(DeclarativeBase):
	pass

class Category(str, PyEnum):
    DEVORCE = "devorce"
    SHISHKA = "shishka"

class BudgetType(str, PyEnum):
    BIG = "big"
    BOMSH = "bomsh"

class RequestStatusType(str, PyEnum):
    OPEN = "open"
    CLOSED = "closed"


class UserRequestBase(Base):
	__tablename__ = "user_request"

	id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    category: Mapped[Category] = mapped_column(
        Enum(Category, name="category"),
        default=Category.DEVORCE
    )
    budget: Mapped[BudgetType] = mapped_column(
        Enum(BudgetType, name="budget"),
        default=BudgetType.BIG
    )
    status: Mapped[RequestStatusType] = mapped_column(
        Enum(RequestStatusType, name="status"),
        default=RequestStatusType.OPEN
    )
	title: Mapped[str] = mapped_column(String())
    description: Mapped[str] = mapped_column(String())
    budget_value: Mapped[int] = mapped_column(Integer(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime())