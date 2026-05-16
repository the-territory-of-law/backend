from __future__ import annotations

import json

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Request,
    Response,
    UploadFile,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dependencies.dependencies import get_current_user
from app.core.database import get_db
from app.modules.chat.connection_manager import deal_chat_manager
from app.modules.chat.participant import deal_exists, is_deal_participant
from app.modules.chat.schemas import (
    ChatAttachmentUploadResponse,
    ChatListItemResponse,
    ChatMessageFullResponse,
    ChatMessagesPageResponse,
    ChatReadThroughRequest,
    ChatReadThroughResponse,
    ChatSendMessageRequest,
    ChatUpdateMessageRequest,
)
from app.modules.chat.service import (
    MessageModerationError,
    create_message,
    create_message_with_uploads,
    list_deal_messages_page,
    list_user_chats,
    mark_inbox_delivered,
    mark_messages_read_through,
    moderation_error_detail,
    save_uploaded_attachment,
    soft_delete_chat_message,
    update_chat_message,
    ws_message_deleted_payload,
    ws_message_updated_payload,
    ws_new_message_payload,
    ws_read_through_payload,
)
from app.modules.users.models import User

router = APIRouter(prefix="/chats", tags=["chat"])


async def _require_deal_chat_access(db: AsyncSession, user_id: int, deal_id: int) -> None:
    if not await deal_exists(db, deal_id):
        raise HTTPException(status_code=404, detail="Deal not found")
    if not await is_deal_participant(db, user_id, deal_id):
        raise HTTPException(status_code=403, detail="Forbidden")


@router.get("", response_model=list[ChatListItemResponse])
async def get_my_chats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
):
    safe_limit = min(max(limit, 1), 100)
    safe_offset = max(offset, 0)
    return await list_user_chats(db, user.id, safe_limit, safe_offset)


@router.get("/{deal_id}/messages", response_model=ChatMessagesPageResponse)
async def get_chat_messages(
    deal_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
):
    await _require_deal_chat_access(db, user.id, deal_id)
    await mark_inbox_delivered(db, deal_id, user.id)
    safe_limit = min(max(limit, 1), 200)
    safe_offset = max(offset, 0)
    return await list_deal_messages_page(db, deal_id, user.id, safe_limit, safe_offset)


@router.post("/{deal_id}/read-through", response_model=ChatReadThroughResponse)
async def mark_chat_read_through(
    deal_id: int,
    payload: ChatReadThroughRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_deal_chat_access(db, user.id, deal_id)
    through_id, read_at, marked = await mark_messages_read_through(
        db, deal_id, user.id, payload.message_id
    )
    await deal_chat_manager.broadcast_json(
        deal_id,
        ws_read_through_payload(through_id, user.id, marked, read_at),
    )
    return ChatReadThroughResponse(
        through_message_id=through_id,
        marked_message_ids=marked,
        read_at=read_at,
    )


@router.post(
    "/{deal_id}/attachments",
    response_model=ChatAttachmentUploadResponse,
    status_code=201,
)
async def upload_chat_attachment(
    deal_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...),
):
    await _require_deal_chat_access(db, user.id, deal_id)
    data = await file.read()
    return await save_uploaded_attachment(
        db,
        deal_id,
        user.id,
        file.filename or "file",
        file.content_type or "application/octet-stream",
        data,
    )


@router.post("/{deal_id}/messages", response_model=ChatMessageFullResponse, status_code=201)
async def send_message_http(
    deal_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_deal_chat_access(db, user.id, deal_id)

    ct = (request.headers.get("content-type") or "").lower()
    text_part: str | None = None
    attachment_ids: list[int] | None = None
    files: list[UploadFile] = []

    if "multipart/form-data" in ct:
        form = await request.form()
        raw_text = form.get("text")
        if isinstance(raw_text, str):
            text_part = raw_text
        elif raw_text is not None:
            text_part = str(raw_text)
        for key in ("attachments", "attachments[]"):
            if key in form:
                vals = form.getlist(key)
                for item in vals:
                    if isinstance(item, UploadFile):
                        files.append(item)
    else:
        try:
            body = await request.json()
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail="Invalid JSON body") from exc
        try:
            payload = ChatSendMessageRequest.model_validate(body)
        except Exception as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        text_part = payload.text
        attachment_ids = list(payload.attachments or [])

    try:
        if files:
            msg = await create_message_with_uploads(db, deal_id, user.id, text_part, files)
        else:
            msg = await create_message(
                db,
                deal_id,
                user.id,
                text_part,
                attachment_ids if attachment_ids else None,
            )
    except MessageModerationError as exc:
        raise HTTPException(
            status_code=422,
            detail=moderation_error_detail(exc.message, exc.reason),
        ) from exc

    await deal_chat_manager.broadcast_json(deal_id, ws_new_message_payload(msg))
    return msg


@router.patch("/messages/{message_id}", response_model=ChatMessageFullResponse)
async def edit_message(
    message_id: int,
    payload: ChatUpdateMessageRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    text_value = payload.text.strip()
    updated = await update_chat_message(db, message_id, user.id, text_value)
    deal_id = updated.deal_id
    await deal_chat_manager.broadcast_json(
        deal_id,
        ws_message_updated_payload(
            message_id=updated.id,
            text=updated.text or "",
            edited_at=updated.edited_at or updated.created_at,
            edit_history=updated.edit_history,
        ),
    )
    return updated


@router.delete("/messages/{message_id}", status_code=204)
async def remove_message(
    message_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    deal_id, deleted_at = await soft_delete_chat_message(db, message_id, user.id)
    await deal_chat_manager.broadcast_json(
        deal_id,
        ws_message_deleted_payload(message_id, deleted_at),
    )
    return Response(status_code=204)
