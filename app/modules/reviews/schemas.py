from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ReviewBase(BaseModel):
    deal_id: int
    rating: int = Field(ge=1, le=5)
    text: Optional[str] = None


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    text: Optional[str] = None


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    deal_id: int
    client_id: int
    lawyer_id: int
    rating: int
    text: Optional[str] = None
    created_at: datetime


class ReviewsPage(BaseModel):
    reviews: list[ReviewResponse]
    total: int
    has_more: bool
