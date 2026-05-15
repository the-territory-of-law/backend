from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ChatSendMessageRequest(BaseModel):
    """JSON-отправка (без файлов). Для файлов — multipart или WS + предзагрузка."""

    text: str | None = Field(default=None, max_length=4000)
    attachments: list[int] | None = Field(
        default=None,
        description="ID вложений после POST /chats/{deal_id}/attachments",
    )


class ChatUpdateMessageRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)


class ChatReadThroughRequest(BaseModel):
    """Все входящие сообщения сделки с id ≤ message_id считаются прочитанными."""

    message_id: int = Field(gt=0)


class ChatReadThroughResponse(BaseModel):
    through_message_id: int
    marked_message_ids: list[int]
    read_at: datetime


class ChatMessageAttachmentResponse(BaseModel):
    id: int
    type: Literal["image", "file"]
    url: str
    filename: str
    size: int
    mime: str
    width: int | None = None
    height: int | None = None
    thumbnail_url: str | None = None


class EditHistoryItemResponse(BaseModel):
    old_text: str | None
    edited_at: datetime


class DeliveryStatusItemResponse(BaseModel):
    user_id: int
    status: Literal["sent", "delivered", "read", "failed"]
    at: datetime


class ChatMessageFullResponse(BaseModel):
    """Сообщение в истории / ответ POST/PATCH — как в API.md."""

    id: int
    deal_id: int
    client_id: int
    sender_id: int
    text: str | None
    attachments: list[ChatMessageAttachmentResponse]
    created_at: datetime
    edited_at: datetime | None
    deleted_at: datetime | None
    edit_history: list[EditHistoryItemResponse]
    delivery_statuses: list[DeliveryStatusItemResponse]
    blocked_reason: str | None = None


class ChatMessagesPageResponse(BaseModel):
    messages: list[ChatMessageFullResponse]
    total: int
    has_more: bool


class ChatAttachmentUploadResponse(BaseModel):
    file_id: int
    url: str
    mime_type: str
    size: int


class ChatListLastMessageAttachment(BaseModel):
    id: int
    type: Literal["image", "file"]
    filename: str
    mime: str


class ChatListLastMessage(BaseModel):
    id: int
    text: str | None
    sender_id: int
    attachments: list[ChatListLastMessageAttachment]
    created_at: datetime


class ChatListItemResponse(BaseModel):
    deal_id: int
    client_id: int
    client_name: str
    client_avatar_url: str | None = None
    lawyer_id: int
    lawyer_name: str
    lawyer_avatar_url: str | None = None
    deal_status: str
    last_message: ChatListLastMessage | None = None
    unread_count: int = 0


ChatDialogResponse = ChatListItemResponse

# Совместимость со старым плоским ответом сообщения
ChatMessageResponse = ChatMessageFullResponse
