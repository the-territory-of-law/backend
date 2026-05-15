from enum import StrEnum
from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict

class OfferStatusType(StrEnum):
    REJECTED = "rejected"
    ACCEPTED = "accepted"
    PENDING = "pending"

class LawyerOfferBase(BaseModel):
    request_id: int
    status: OfferStatusType = OfferStatusType.PENDING
    what_included: str
    price: int
    term: date

class LawyerOfferCreate(LawyerOfferBase):
    pass

class LawyerOfferUpdate(BaseModel):
    status: Optional[OfferStatusType] = None
    what_included: Optional[str] = None
    price: Optional[int] = None
    term: Optional[date] = None

class LawyerOfferResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    request_id: int
    lawyer_id: int
    status: OfferStatusType
    what_included: str
    price: int
    term: date