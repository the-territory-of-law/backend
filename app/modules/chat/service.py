from __future__ import annotations

import uuid
from collections import defaultdict
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from fastapi import HTTPException, UploadFile
from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.modules.chat.models import (
    ChatAttachment,
    ChatAttachmentKind,
    ChatDeliveryStatus,
    ChatMessage,
    ChatMessageDeliveryStatus,
    ChatMessageEditHistory,
)
from app.modules.chat.connection_manager import deal_chat_manager
from app.modules.chat.off_platform_guard import OffPlatformResult, check_off_platform
from app.modules.chat.repository import ChatRepository
from app.modules.chat.schemas import (
    ChatAttachmentUploadResponse,
    ChatListItemResponse,
    ChatListLastMessage,
    ChatListLastMessageAttachment,
    ChatMessageAttachmentResponse,
    ChatMessageFullResponse,
    ChatMessagesPageResponse,
    DeliveryStatusItemResponse,
    EditHistoryItemResponse,
)
from app.modules.deals.models import DealStatusType

settings = Settings()


class MessageModerationError(Exception):
    """Текст не прошёл модерацию; сообщение сохранено у отправителя со статусом failed."""

    def __init__(self, message: ChatMessageFullResponse, reason: str) -> None:
        self.message = message
        self.reason = reason
        super().__init__(reason)


def moderation_error_detail(
    message: ChatMessageFullResponse,
    reason: str,
) -> dict[str, Any]:
    return {
        "code": "message_failed",
        "status": "failed",
        "reason": reason,
        "blocked_reason": reason,
        "message": message.model_dump(mode="json"),
    }


def _deal_status_for_list(raw: object) -> str:
    if raw is None:
        return "active"
    if isinstance(raw, DealStatusType):
        v = raw.value
    else:
        v = str(getattr(raw, "value", raw))
    s = str(v).lower()
    if s == "in_progress":
        return "active"
    return str(v) if v else "active"


def _attachment_type_for_list(kind: object) -> Literal["image", "file"]:
    v = getattr(kind, "value", kind)
    s = str(v).lower()
    if s == "image":
        return "image"
    return "file"


def _norm_delivery_status(s: object) -> Literal["sent", "delivered", "read", "failed"]:
    if isinstance(s, ChatDeliveryStatus):
        x = s.value
    else:
        x = str(getattr(s, "value", s)).lower()
    if x in ("sent", "delivered", "read", "failed"):
        return x  # type: ignore[return-value]
    return "sent"


def _norm_attachment_type_from_mime(mime: str) -> ChatAttachmentKind:
    return (
        ChatAttachmentKind.IMAGE
        if mime.lower().startswith("image/")
        else ChatAttachmentKind.FILE
    )


def _public_file_url(deal_id: int, stored_name: str) -> str:
    mount = settings.CHAT_STATIC_MOUNT.rstrip("/")
    base = (settings.CHAT_PUBLIC_BASE_URL or "").rstrip("/")
    path = f"{mount}/{deal_id}/{stored_name}"
    if base:
        return f"{base}{path}" if path.startswith("/") else f"{base}/{path}"
    return f"/{path.lstrip('/')}"


def _rows_to_full_messages(
    message_rows: Sequence[Row[Any]],
    attachments_by_msg: dict[int, list[ChatMessageAttachmentResponse]],
    history_by_msg: dict[int, list[EditHistoryItemResponse]],
    delivery_by_msg: dict[int, list[DeliveryStatusItemResponse]],
) -> list[ChatMessageFullResponse]:
    out: list[ChatMessageFullResponse] = []
    for row in message_rows:
        data = row._mapping
        mid = int(data["id"])
        out.append(
            ChatMessageFullResponse(
                id=mid,
                deal_id=int(data["deal_id"]),
                client_id=int(data["client_id"]),
                sender_id=int(data["sender_id"]),
                text=data.get("text"),
                attachments=list(attachments_by_msg.get(mid, [])),
                created_at=data["sent_at"],
                edited_at=data.get("edited_at"),
                deleted_at=data.get("deleted_at"),
                edit_history=list(history_by_msg.get(mid, [])),
                delivery_statuses=list(delivery_by_msg.get(mid, [])),
                blocked_reason=data.get("blocked_reason"),
            )
        )
    return out


async def check_message_text_moderation(text: str) -> OffPlatformResult:
    return await check_off_platform(text, settings)


async def create_moderation_failed_message(
    session: AsyncSession,
    deal_id: int,
    sender_id: int,
    text: str,
    reason: str,
) -> ChatMessageFullResponse:
    repo = ChatRepository(session)
    client_id = await _deal_client_id(repo, deal_id)
    sent_at = datetime.now(timezone.utc)
    text_norm = text.strip()

    msg = ChatMessage(
        deal_id=deal_id,
        client_id=client_id,
        sender_id=sender_id,
        text=text_norm,
        blocked_reason=reason[:512],
        sent_at=sent_at,
    )
    await repo.add_and_flush(msg)
    message_id = int(msg.id)
    await repo.add_delivery_status(
        ChatMessageDeliveryStatus(
            message_id=message_id,
            user_id=sender_id,
            status=ChatDeliveryStatus.FAILED,
            at=sent_at,
        )
    )
    await session.commit()
    return await build_message_full(session, message_id)


async def ensure_text_allowed_or_fail(
    session: AsyncSession,
    deal_id: int,
    sender_id: int,
    text: str,
) -> None:
    guard = await check_message_text_moderation(text)
    if not guard.blocked:
        return
    reason = guard.reason or "Политика платформы: общение только в этом чате."
    failed_msg = await create_moderation_failed_message(
        session, deal_id, sender_id, text, reason
    )
    raise MessageModerationError(failed_msg, reason)


async def _batch_map_message_children(
    repo: ChatRepository, message_ids: list[int]
) -> tuple[
    dict[int, list[ChatMessageAttachmentResponse]],
    dict[int, list[EditHistoryItemResponse]],
    dict[int, list[DeliveryStatusItemResponse]],
]:
    if not message_ids:
        return {}, {}, {}

    att_by: dict[int, list[ChatMessageAttachmentResponse]] = defaultdict(list)
    hist_by: dict[int, list[EditHistoryItemResponse]] = defaultdict(list)
    del_by: dict[int, list[DeliveryStatusItemResponse]] = defaultdict(list)

    for att in await repo.fetch_attachments_for_message_ids(message_ids):
        att_by[int(att.message_id)].append(
            ChatMessageAttachmentResponse(
                id=int(att.id),
                type=_attachment_type_for_list(att.kind),
                url=str(att.url),
                filename=str(att.filename),
                size=int(att.size or 0),
                mime=str(att.mime),
                width=att.width,
                height=att.height,
                thumbnail_url=att.thumbnail_url,
            )
        )

    for h in await repo.fetch_edit_histories_for_message_ids(message_ids):
        hist_by[int(h.message_id)].append(
            EditHistoryItemResponse(old_text=h.old_text, edited_at=h.edited_at)
        )

    for d in await repo.fetch_delivery_statuses_for_message_ids(message_ids):
        del_by[int(d.message_id)].append(
            DeliveryStatusItemResponse(
                user_id=int(d.user_id),
                status=_norm_delivery_status(d.status),
                at=d.at,
            )
        )

    return att_by, hist_by, del_by


async def _deal_client_id(repo: ChatRepository, deal_id: int) -> int:
    cid = await repo.get_deal_client_id(deal_id)
    if cid is None:
        raise HTTPException(status_code=404, detail="Deal not found")
    return int(cid)


async def _deal_participants(repo: ChatRepository, deal_id: int) -> tuple[int, int]:
    pair = await repo.get_deal_participant_user_ids(deal_id)
    if pair is None:
        raise HTTPException(status_code=404, detail="Deal not found")
    return pair


async def _insert_delivery_for_recipients(
    repo: ChatRepository,
    message_id: int,
    deal_id: int,
    sender_id: int,
    at: datetime,
) -> None:
    client_uid, lawyer_uid = await _deal_participants(repo, deal_id)
    for uid in (client_uid, lawyer_uid):
        if uid == sender_id:
            continue
        await repo.add_delivery_status(
            ChatMessageDeliveryStatus(
                message_id=message_id,
                user_id=uid,
                status=ChatDeliveryStatus.SENT,
                at=at,
            )
        )


async def _recipient_user_id(
    repo: ChatRepository, deal_id: int, sender_id: int
) -> int:
    client_uid, lawyer_uid = await _deal_participants(repo, deal_id)
    return lawyer_uid if sender_id == client_uid else client_uid


async def _apply_delivered_if_recipient_online(
    repo: ChatRepository,
    deal_id: int,
    sender_id: int,
    message_id: int,
    at: datetime,
) -> None:
    recipient_id = await _recipient_user_id(repo, deal_id, sender_id)
    if deal_chat_manager.is_user_connected(deal_id, recipient_id):
        await repo.try_mark_message_delivered(message_id, recipient_id, at)


async def mark_inbox_delivered(
    session: AsyncSession,
    deal_id: int,
    user_id: int,
) -> list[int]:
    """Все входящие со статусом sent → delivered (открытие чата / подключение WS)."""
    repo = ChatRepository(session)
    at = datetime.now(timezone.utc)
    updated = await repo.mark_sent_as_delivered_in_deal(deal_id, user_id, at)
    if updated:
        await session.commit()
    return updated


async def build_message_full(session: AsyncSession, message_id: int) -> ChatMessageFullResponse:
    repo = ChatRepository(session)
    row = await repo.fetch_message_core_row(message_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Message not found")
    att_by, hist_by, del_by = await _batch_map_message_children(repo, [message_id])
    return _rows_to_full_messages([row], att_by, hist_by, del_by)[0]


async def list_user_chats(
    session: AsyncSession,
    user_id: int,
    limit: int,
    offset: int,
) -> list[ChatListItemResponse]:
    repo = ChatRepository(session)
    rows = await repo.fetch_chats_list_rows(user_id, limit, offset)
    if not rows:
        return []

    last_ids = [
        int(m["last_message_id"])
        for m in (r._mapping for r in rows)
        if m.get("last_message_id") is not None
    ]
    attachments_by_msg: dict[int, list[ChatListLastMessageAttachment]] = defaultdict(list)
    if last_ids:
        for att in await repo.fetch_attachments_for_message_ids(last_ids):
            mid = int(att.message_id)
            t = _attachment_type_for_list(att.kind)
            attachments_by_msg[mid].append(
                ChatListLastMessageAttachment(
                    id=int(att.id),
                    type=t,
                    filename=str(att.filename),
                    mime=str(att.mime),
                )
            )

    deal_ids = [int(r._mapping["deal_id"]) for r in rows]
    unread_by_deal = await repo.fetch_unread_counts_by_deals(deal_ids, user_id)

    out: list[ChatListItemResponse] = []
    for row in rows:
        data = row._mapping
        deal_id = int(data["deal_id"])
        lm_id = data.get("last_message_id")
        last_msg: ChatListLastMessage | None = None
        if lm_id is not None:
            lm_id_int = int(lm_id)
            last_msg = ChatListLastMessage(
                id=lm_id_int,
                text=data.get("last_message_text"),
                sender_id=int(data["last_message_sender_id"]),
                attachments=list(attachments_by_msg.get(lm_id_int, [])),
                created_at=data["last_message_sent_at"],
            )
        out.append(
            ChatListItemResponse(
                deal_id=deal_id,
                client_id=int(data["client_id"]),
                client_name=(data.get("client_name") or "") or "",
                client_avatar_url=None,
                lawyer_id=int(data["lawyer_id"]),
                lawyer_name=(data.get("lawyer_name") or "") or "",
                lawyer_avatar_url=None,
                deal_status=_deal_status_for_list(data.get("deal_status")),
                last_message=last_msg,
                unread_count=unread_by_deal.get(deal_id, 0),
            )
        )
    return out


async def list_deal_messages_page(
    session: AsyncSession,
    deal_id: int,
    viewer_user_id: int,
    limit: int,
    offset: int,
) -> ChatMessagesPageResponse:
    repo = ChatRepository(session)
    total = await repo.count_messages_for_deal(deal_id, viewer_user_id)
    msg_rows = await repo.fetch_messages_page_rows(deal_id, viewer_user_id, limit, offset)
    ids = [int(r._mapping["id"]) for r in msg_rows]
    att_by, hist_by, del_by = await _batch_map_message_children(repo, ids)
    messages = _rows_to_full_messages(msg_rows, att_by, hist_by, del_by)
    has_more = offset + len(messages) < total
    return ChatMessagesPageResponse(messages=messages, total=total, has_more=has_more)


async def create_message(
    session: AsyncSession,
    deal_id: int,
    sender_id: int,
    text: str | None,
    attachment_ids: list[int] | None,
) -> ChatMessageFullResponse:
    repo = ChatRepository(session)
    text_norm = text.strip() if isinstance(text, str) else None
    if text_norm == "":
        text_norm = None
    ids = list(attachment_ids or [])
    if text_norm is None and not ids:
        raise HTTPException(
            status_code=400,
            detail="Message must have non-empty text or at least one attachment",
        )

    if text_norm:
        await ensure_text_allowed_or_fail(session, deal_id, sender_id, text_norm)

    client_id = await _deal_client_id(repo, deal_id)
    sent_at = datetime.now(timezone.utc)

    msg = ChatMessage(
        deal_id=deal_id,
        client_id=client_id,
        sender_id=sender_id,
        text=text_norm,
        blocked_reason=None,
        sent_at=sent_at,
    )
    await repo.add_and_flush(msg)
    message_id = int(msg.id)

    if ids:
        cnt = await repo.count_pending_attachments(ids, deal_id, sender_id)
        if cnt != len(ids):
            await session.rollback()
            raise HTTPException(
                status_code=400,
                detail="Some attachment ids are invalid or already linked",
            )
        await repo.link_pending_attachments_to_message(ids, deal_id, sender_id, message_id)

    await _insert_delivery_for_recipients(repo, message_id, deal_id, sender_id, sent_at)
    await session.flush()
    await _apply_delivered_if_recipient_online(
        repo, deal_id, sender_id, message_id, sent_at
    )
    await session.commit()
    return await build_message_full(session, message_id)


async def save_uploaded_attachment(
    session: AsyncSession,
    deal_id: int,
    user_id: int,
    filename: str,
    mime: str,
    data: bytes,
) -> ChatAttachmentUploadResponse:
    if len(data) > settings.CHAT_MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large")

    repo = ChatRepository(session)
    kind = _norm_attachment_type_from_mime(mime)
    stored = f"{uuid.uuid4().hex}_{filename}"
    deal_dir = Path(settings.CHAT_UPLOAD_DIR) / str(deal_id)
    deal_dir.mkdir(parents=True, exist_ok=True)
    path = deal_dir / stored
    path.write_bytes(data)

    url = _public_file_url(deal_id, stored)
    att = ChatAttachment(
        message_id=None,
        deal_id=deal_id,
        uploaded_by_id=user_id,
        kind=kind,
        url=url,
        filename=filename,
        size=len(data),
        mime=mime,
    )
    await repo.add_and_flush(att)
    await session.commit()
    return ChatAttachmentUploadResponse(
        file_id=int(att.id), url=url, mime_type=mime, size=len(data)
    )


async def create_message_with_uploads(
    session: AsyncSession,
    deal_id: int,
    sender_id: int,
    text: str | None,
    files: list[UploadFile],
) -> ChatMessageFullResponse:
    repo = ChatRepository(session)
    parts: list[tuple[str, str, bytes]] = []
    for uf in files:
        raw = await uf.read()
        if len(raw) > settings.CHAT_MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="File too large")
        mime = uf.content_type or "application/octet-stream"
        parts.append((uf.filename or "file", mime, raw))

    text_norm = text.strip() if isinstance(text, str) else None
    if text_norm == "":
        text_norm = None
    if text_norm is None and not parts:
        raise HTTPException(
            status_code=400,
            detail="Message must have non-empty text or at least one attachment",
        )

    if text_norm:
        await ensure_text_allowed_or_fail(session, deal_id, sender_id, text_norm)

    client_id = await _deal_client_id(repo, deal_id)
    sent_at = datetime.now(timezone.utc)

    msg = ChatMessage(
        deal_id=deal_id,
        client_id=client_id,
        sender_id=sender_id,
        text=text_norm,
        blocked_reason=None,
        sent_at=sent_at,
    )
    await repo.add_and_flush(msg)
    message_id = int(msg.id)

    for fname, mime, raw in parts:
        kind = _norm_attachment_type_from_mime(mime)
        stored = f"{uuid.uuid4().hex}_{fname}"
        deal_dir = Path(settings.CHAT_UPLOAD_DIR) / str(deal_id)
        deal_dir.mkdir(parents=True, exist_ok=True)
        path = deal_dir / stored
        path.write_bytes(raw)
        url = _public_file_url(deal_id, stored)
        await repo.add_and_flush(
            ChatAttachment(
                message_id=message_id,
                deal_id=deal_id,
                uploaded_by_id=sender_id,
                kind=kind,
                url=url,
                filename=fname,
                size=len(raw),
                mime=mime,
            )
        )

    await _insert_delivery_for_recipients(repo, message_id, deal_id, sender_id, sent_at)
    await session.flush()
    await _apply_delivered_if_recipient_online(
        repo, deal_id, sender_id, message_id, sent_at
    )
    await session.commit()
    return await build_message_full(session, message_id)


async def update_chat_message(
    session: AsyncSession,
    message_id: int,
    sender_id: int,
    text_value: str,
) -> ChatMessageFullResponse:
    repo = ChatRepository(session)
    text_stripped = text_value.strip()
    if not text_stripped:
        raise HTTPException(status_code=400, detail="Empty text")

    msg_row = await repo.get_message(message_id)
    if msg_row is None:
        raise HTTPException(status_code=404, detail="Message not found")
    if msg_row.sender_id != sender_id or msg_row.deleted_at is not None:
        raise HTTPException(status_code=403, detail="Cannot edit another user's message")

    guard = await check_message_text_moderation(text_stripped)
    if guard.blocked:
        reason = guard.reason or "Политика платформы: общение только в этом чате."
        raise HTTPException(
            status_code=422,
            detail={
                "code": "message_failed",
                "status": "failed",
                "reason": reason,
                "blocked_reason": reason,
            },
        )

    old_text = msg_row.text

    edited_at = datetime.now(timezone.utc)
    await repo.add_edit_history(
        ChatMessageEditHistory(
            message_id=message_id,
            old_text=old_text,
            edited_at=edited_at,
        )
    )

    msg_row.text = text_stripped
    msg_row.edited_at = edited_at
    await session.commit()
    return await build_message_full(session, message_id)


async def soft_delete_chat_message(
    session: AsyncSession,
    message_id: int,
    sender_id: int,
) -> tuple[int, datetime]:
    repo = ChatRepository(session)
    msg = await repo.get_message(message_id)
    if msg is None:
        raise HTTPException(status_code=404, detail="Message not found")
    if msg.sender_id != sender_id or msg.deleted_at is not None:
        raise HTTPException(status_code=403, detail="Cannot delete another user's message")
    deal_id = int(msg.deal_id)
    deleted_at = datetime.now(timezone.utc)
    msg.deleted_at = deleted_at
    await session.commit()
    return deal_id, deleted_at


async def get_message_deal_id(session: AsyncSession, message_id: int) -> int:
    repo = ChatRepository(session)
    deal_id = await repo.get_message_deal_id(message_id)
    if deal_id is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return int(deal_id)


async def mark_message_read(
    session: AsyncSession,
    deal_id: int,
    user_id: int,
    message_id: int,
) -> tuple[int, datetime, str]:
    repo = ChatRepository(session)
    mid_deal = await repo.get_message_deal_id(message_id)
    if mid_deal is None:
        raise HTTPException(status_code=404, detail="Message not found")
    if int(mid_deal) != deal_id:
        raise HTTPException(status_code=400, detail="Message does not belong to this deal")

    at = datetime.now(timezone.utc)
    existing = await repo.get_delivery_status(message_id, user_id)
    if existing is None:
        await repo.add_delivery_status(
            ChatMessageDeliveryStatus(
                message_id=message_id,
                user_id=user_id,
                status=ChatDeliveryStatus.READ,
                at=at,
            )
        )
    else:
        existing.status = ChatDeliveryStatus.READ
        existing.at = at
    await session.commit()
    return message_id, at, "read"


async def mark_messages_read_through(
    session: AsyncSession,
    deal_id: int,
    user_id: int,
    message_id: int,
) -> tuple[int, datetime, list[int]]:
    repo = ChatRepository(session)
    mid_deal = await repo.get_message_deal_id(message_id)
    if mid_deal is None:
        raise HTTPException(status_code=404, detail="Message not found")
    if int(mid_deal) != deal_id:
        raise HTTPException(status_code=400, detail="Message does not belong to this deal")

    at = datetime.now(timezone.utc)
    affected = await repo.apply_read_through_statuses(deal_id, user_id, message_id, at)
    await session.commit()
    return message_id, at, affected


def ws_new_message_payload(msg: ChatMessageFullResponse) -> dict[str, Any]:
    return {"type": "new_message", "message": msg.model_dump(mode="json")}


def ws_message_updated_payload(
    message_id: int,
    text: str,
    edited_at: datetime,
    edit_history: list[EditHistoryItemResponse],
) -> dict[str, Any]:
    return {
        "type": "message_updated",
        "message_id": message_id,
        "text": text,
        "edited_at": edited_at.isoformat(),
        "edit_history": [h.model_dump(mode="json") for h in edit_history],
    }


def ws_message_deleted_payload(message_id: int, deleted_at: datetime) -> dict[str, Any]:
    return {
        "type": "message_deleted",
        "message_id": message_id,
        "deleted_at": deleted_at.isoformat(),
    }


def ws_status_payload(message_id: int, user_id: int, status: str, at: datetime) -> dict[str, Any]:
    return {
        "type": "status",
        "message_id": message_id,
        "user_id": user_id,
        "status": status,
        "at": at.isoformat(),
    }


def ws_read_through_payload(
    through_message_id: int,
    reader_user_id: int,
    message_ids: list[int],
    at: datetime,
) -> dict[str, Any]:
    return {
        "type": "read_through",
        "through_message_id": through_message_id,
        "user_id": reader_user_id,
        "message_ids": message_ids,
        "at": at.isoformat(),
    }


def ws_message_failed_payload(
    message: ChatMessageFullResponse,
    reason: str,
) -> dict[str, Any]:
    return {
        "type": "message_failed",
        "status": "failed",
        "reason": reason,
        "blocked_reason": reason,
        "message": message.model_dump(mode="json"),
    }


def ws_typing_payload(user_id: int, *, stop: bool = False) -> dict[str, Any]:
    return {"type": "stop_typing" if stop else "typing", "user_id": user_id}
