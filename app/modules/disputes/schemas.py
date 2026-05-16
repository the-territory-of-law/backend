from datetime import datetime
from enum import StrEnum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class DisputeStatusType(StrEnum):
    OPEN = "open"
    RESOLVED = "resolved"


class DisputeResolutionStatusType(StrEnum):
    CLIENT_WIN = "client_win"
    LAWYER_WIN = "lawyer_win"
    DRAW = "draw"


class DisputeBase(BaseModel):
    deal_id: int
    reason: str = Field(min_length=1)


class DisputeCreate(DisputeBase):
    pass


class DisputeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    deal_id: int
    opened_by: int
    status: DisputeStatusType
    reason: str
    resolution: DisputeResolutionStatusType
    created_at: datetime
    assigned_admin_id: Optional[int] = None


class DisputesPage(BaseModel):
    disputes: list[DisputeResponse]
    total: int
    has_more: bool


class DisputeMessageCreate(BaseModel):
    text: Optional[str] = None
    attachment_ids: Optional[list[int]] = None


class FileMetaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    filename: str
    mime: str
    size: int


class DisputeMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dispute_id: int
    author_id: int
    text: str
    attachments: list[FileMetaResponse] = []
    created_at: datetime


class TimelineEventResponse(BaseModel):
    type: str
    at: datetime
    actor_id: int
    payload: dict[str, Any] = {}


class DisputeTimelineResponse(BaseModel):
    events: list[TimelineEventResponse] = []


class DisputeAssignRequest(BaseModel):
    admin_user_id: int


class DisputeRequestInfoCreate(BaseModel):
    text: str = Field(min_length=1)
    deadline_at: datetime


class DisputeResolveRequest(BaseModel):
    resolution: DisputeResolutionStatusType
    refund_amount: Optional[int] = Field(default=None, ge=0)
    comment: Optional[str] = None


class DisputeRejectRequest(BaseModel):
    reason: str = Field(min_length=1)
