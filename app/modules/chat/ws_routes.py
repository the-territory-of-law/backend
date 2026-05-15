import json
import logging

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.database import SessionLocal
from app.core.security import decode_access_token_user_id
from app.modules.chat.connection_manager import deal_chat_manager
from app.modules.chat.participant import is_deal_participant
from app.modules.chat.service import (
    MessageModerationError,
    create_message,
    mark_inbox_delivered,
    mark_message_read,
    mark_messages_read_through,
    moderation_error_detail,
    ws_message_failed_payload,
    ws_new_message_payload,
    ws_read_through_payload,
    ws_status_payload,
    ws_typing_payload,
)
from app.modules.users.models import User

logger = logging.getLogger(__name__)
settings = Settings()
router = APIRouter(tags=["chat-realtime"])


def _access_token_from_websocket(websocket: WebSocket) -> str | None:
    token = websocket.query_params.get("token")
    if token:
        return token
    return websocket.cookies.get(settings.COOKIE_NAME)


async def _authorize_deal_chat(
    db: AsyncSession, websocket: WebSocket, deal_id: int
) -> tuple[int, User] | None:
    token = _access_token_from_websocket(websocket)
    if not token:
        await websocket.close(code=4001, reason="Not authenticated")
        return None
    user_id = decode_access_token_user_id(token)
    if user_id is None:
        await websocket.close(code=4001, reason="Invalid access token")
        return None
    if not await is_deal_participant(db, user_id, deal_id):
        await websocket.close(code=4003, reason="Forbidden")
        return None
    user = await db.get(User, user_id)
    if not user:
        await websocket.close(code=4001, reason="User not found")
        return None
    return user_id, user


def _ws_error(message: str) -> dict:
    return {"type": "error", "message": message}


@router.websocket("/ws/deals/{deal_id}/chat")
async def deal_chat_websocket(websocket: WebSocket, deal_id: int) -> None:
    async with SessionLocal() as db:
        auth = await _authorize_deal_chat(db, websocket, deal_id)
        if auth is None:
            return
        user_id, _user = auth

        await deal_chat_manager.connect(deal_id, user_id, websocket)
        await mark_inbox_delivered(db, deal_id, user_id)
        try:
            while True:
                raw = await websocket.receive_text()
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    await websocket.send_json(
                        {"type": "error", "detail": "invalid_json", "message": "invalid_json"}
                    )
                    continue

                msg_type = data.get("type")
                if msg_type == "ping":
                    await websocket.send_json({"type": "pong"})
                    continue

                if msg_type == "typing":
                    await deal_chat_manager.broadcast_json(
                        deal_id,
                        ws_typing_payload(user_id, stop=False),
                        exclude_user_id=user_id,
                    )
                    continue

                if msg_type == "stop_typing":
                    await deal_chat_manager.broadcast_json(
                        deal_id,
                        ws_typing_payload(user_id, stop=True),
                        exclude_user_id=user_id,
                    )
                    continue

                if msg_type == "read":
                    mid = data.get("message_id")
                    if mid is None:
                        await websocket.send_json(_ws_error("message_id required"))
                        continue
                    try:
                        mid_int = int(mid)
                    except (TypeError, ValueError):
                        await websocket.send_json(_ws_error("message_id required"))
                        continue
                    try:
                        m_id, at, st = await mark_message_read(db, deal_id, user_id, mid_int)
                    except HTTPException as exc:
                        det = exc.detail
                        msg = det if isinstance(det, str) else str(det)
                        await websocket.send_json(_ws_error(msg))
                        continue
                    except Exception as exc:
                        logger.warning("read failed: %s", exc)
                        await websocket.send_json(_ws_error(str(exc)))
                        continue
                    await deal_chat_manager.broadcast_json(
                        deal_id,
                        ws_status_payload(m_id, user_id, st, at),
                    )
                    continue

                if msg_type == "read_through":
                    mid = data.get("message_id")
                    if mid is None:
                        await websocket.send_json(_ws_error("message_id required"))
                        continue
                    try:
                        mid_int = int(mid)
                    except (TypeError, ValueError):
                        await websocket.send_json(_ws_error("message_id required"))
                        continue
                    try:
                        through_id, at_rt, marked = await mark_messages_read_through(
                            db, deal_id, user_id, mid_int
                        )
                    except HTTPException as exc:
                        det = exc.detail
                        msg = det if isinstance(det, str) else str(det)
                        await websocket.send_json(_ws_error(msg))
                        continue
                    except Exception as exc:
                        logger.warning("read_through failed: %s", exc)
                        await websocket.send_json(_ws_error(str(exc)))
                        continue
                    await deal_chat_manager.broadcast_json(
                        deal_id,
                        ws_read_through_payload(through_id, user_id, marked, at_rt),
                    )
                    continue

                if msg_type == "message":
                    body = data.get("data") or {}
                    text_raw = body.get("text")
                    text = text_raw.strip() if isinstance(text_raw, str) else None
                    if text == "":
                        text = None
                    att_ids = body.get("attachment_ids") or []
                    if not isinstance(att_ids, list):
                        att_ids = []
                    att_ids_int: list[int] = []
                    for x in att_ids:
                        if isinstance(x, int):
                            att_ids_int.append(x)
                        elif isinstance(x, str) and x.isdigit():
                            att_ids_int.append(int(x))
                    if text is None and not att_ids_int:
                        await websocket.send_json(
                            _ws_error("Текст пустой и вложения не переданы")
                        )
                        continue
                    try:
                        msg = await create_message(
                            db,
                            deal_id,
                            user_id,
                            text,
                            att_ids_int if att_ids_int else None,
                        )
                    except MessageModerationError as exc:
                        err = moderation_error_detail(exc.message, exc.reason)
                        await websocket.send_json({"type": "error", **err})
                        await websocket.send_json(
                            ws_message_failed_payload(exc.message, exc.reason)
                        )
                        continue
                    except HTTPException as exc:
                        det = exc.detail
                        msg_txt = det if isinstance(det, str) else str(det)
                        await websocket.send_json(_ws_error(msg_txt))
                        continue
                    except Exception as exc:
                        logger.exception("ws message create failed")
                        await websocket.send_json(_ws_error(str(exc)))
                        continue
                    await deal_chat_manager.broadcast_json(
                        deal_id,
                        ws_new_message_payload(msg),
                    )
                    continue

                await websocket.send_json(
                    {"type": "error", "detail": "unknown_type", "message": "unknown_type"}
                )
        except WebSocketDisconnect:
            logger.debug("ws disconnect deal_id=%s user_id=%s", deal_id, user_id)
        finally:
            await deal_chat_manager.disconnect(deal_id, user_id, websocket)
