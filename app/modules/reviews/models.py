from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.orm_base import Base


class Review(Base):
    __tablename__ = "review"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    deal_id: Mapped[int] = mapped_column(ForeignKey("deal.id"))
    client_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    lawyer_id: Mapped[int] = mapped_column(ForeignKey("lawyer_profile.id"))
    rating: Mapped[int] = mapped_column(Integer())
    text: Mapped[str | None] = mapped_column(String(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
