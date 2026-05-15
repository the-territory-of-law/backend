from enum import StrEnum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

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
    status: RequestStatusType = RequestStatusType.OPEN
    title: str
    description: str
    budget_value: Optional[int] = None

class UserRequestCreate(UserRequestBase):
    pass

class UserRequestUpdate(BaseModel):
    category: Optional[RequestCategory] = None
    budget: Optional[RequestBudgetType] = None
    status: Optional[RequestStatusType] = None
    title: Optional[str] = None
    description: Optional[str] = None
    budget_value: Optional[int] = None

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

