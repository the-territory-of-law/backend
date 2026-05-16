from datetime import datetime
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class VerificationStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class PracticeAreaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class LawyerProfileBase(BaseModel):
    city: Optional[str] = None
    about: Optional[str] = None
    experience_years: Optional[int] = Field(default=None, ge=0)
    practice_area_ids: Optional[list[int]] = None


class LawyerProfileCreate(LawyerProfileBase):
    pass


class LawyerProfileUpdate(BaseModel):
    city: Optional[str] = None
    about: Optional[str] = None
    experience_years: Optional[int] = Field(default=None, ge=0)
    practice_area_ids: Optional[list[int]] = None


class LawyerProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    city: Optional[str] = None
    about: Optional[str] = None
    experience_years: Optional[int] = None
    verification_status: VerificationStatus
    practice_areas: list[PracticeAreaResponse] = []
    rating_avg: Optional[float] = None
    reviews_count: Optional[int] = None


class LawyerProfilesPage(BaseModel):
    profiles: list[LawyerProfileResponse]
    total: int
    has_more: bool


class VerificationInfoResponse(BaseModel):
    status: VerificationStatus
    comment: Optional[str] = None
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None


class DiplomUploadResponse(BaseModel):
    diploma_file_id: int
    verification_status: VerificationStatus
