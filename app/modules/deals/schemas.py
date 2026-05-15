from enum import StrEnum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class DealStatusType(StrEnum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class DealBase(BaseModel):
    request_id: int
    offer_id: int
    status: DealStatusType = DealStatusType.IN_PROGRESS
    amount: int
    platform_fee: int
    lawyer_amount: int
    paid_at: datetime #????

class DealCreate(DealBase):
    pass

class DealUpdate(BaseModel):
    status: Optional[DealStatusType] = None
    amount: Optional[int] = None
    platform_fee: Optional[int] = None
    lawyer_amount: Optional[int] = None
    paid_at: Optional[datetime] = None #????

class DealResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    request_id: int
    offer_id: int
    status: DealStatusType
    amount: int
    platform_fee: int
    lawyer_amount: int
    paid_at: datetime