from datetime import datetime
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RequestCategory(StrEnum):
    DEVORCE = "devorce"
    SHISHKA = "shishka"


class RequestBudgetType(StrEnum):
    BIG = "big"
    BOMSH = "bomsh"


class RequestStatusType(StrEnum):
    OPEN = "open"
    CLOSED = "closed"


class UserRequestBase(BaseModel):
    category: RequestCategory
    budget: RequestBudgetType
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    budget_value: Optional[int] = Field(default=None, ge=0)


class UserRequestCreate(UserRequestBase):
    pass


class UserRequestUpdate(BaseModel):
    category: Optional[RequestCategory] = None
    budget: Optional[RequestBudgetType] = None
    title: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = Field(default=None, min_length=1)
    budget_value: Optional[int] = Field(default=None, ge=0)


class UserRequestClose(BaseModel):
    reason: Optional[str] = None


class UserRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    category: RequestCategory
    budget: RequestBudgetType
    status: RequestStatusType
    title: str
    description: str
    budget_value: Optional[int] = None
    created_at: datetime


class UserRequestsPageResponse(BaseModel):
    requests: list[UserRequestResponse]
    total: int
    has_more: bool
