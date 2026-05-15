from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.orm_base import Base


class Category(str, Enum):
    DEVORCE = "devorce"
    SHISHKA = "shishka"


class BudgetType(str, Enum):
    BIG = "big"
    BOMSH = "bomsh"


class RequestStatusType(str, Enum):
    OPEN = "open"
    CLOSED = "closed"


class UserRequest(Base):
    __tablename__ = "user_request"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    category: Mapped[Category] = mapped_column(
        SAEnum(Category, name="category", native_enum=False),
        default=Category.DEVORCE,
    )
    budget: Mapped[BudgetType] = mapped_column(
        SAEnum(BudgetType, name="budget", native_enum=False),
        default=BudgetType.BIG,
    )
    status: Mapped[RequestStatusType] = mapped_column(
        SAEnum(RequestStatusType, name="request_status", native_enum=False),
        default=RequestStatusType.OPEN,
    )
    title: Mapped[str] = mapped_column(String())
    description: Mapped[str] = mapped_column(Text())
    budget_value: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
