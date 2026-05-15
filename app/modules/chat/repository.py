"""Доступ к данным чата (SQLAlchemy 2.0, без HTTP / Pydantic)."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import Row, case, exists, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.modules.chat.models import (
    ChatAttachment,
    ChatDeliveryStatus,
    ChatMessage,
    ChatMessageDeliveryStatus,
    ChatMessageEditHistory,
)
from app.modules.deals.models import Deal
from app.modules.lawyer_profiles.models import LawyerProfile
from app.modules.offers.models import LawyerOffer
from app.modules.requests.models import UserRequest
from app.modules.users.models import User


def _message_visible_to_viewer(viewer_user_id: int):
    return or_(
        ChatMessage.blocked_reason.is_(None),
        ChatMessage.sender_id == viewer_user_id,
    )


class ChatRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_deal_client_id(self, deal_id: int) -> int | None:
        stmt = (
            select(UserRequest.client_id)
            .select_from(Deal)
            .join(UserRequest, UserRequest.id == Deal.request_id)
            .where(Deal.id == deal_id)
            .limit(1)
        )
        return (await self._session.execute(stmt)).scalar_one_or_none()

    async def get_deal_participant_user_ids(self, deal_id: int) -> tuple[int, int] | None:
        stmt = (
            select(UserRequest.client_id, LawyerProfile.user_id)
            .select_from(Deal)
            .join(UserRequest, UserRequest.id == Deal.request_id)
            .join(LawyerOffer, LawyerOffer.id == Deal.offer_id)
            .join(LawyerProfile, LawyerProfile.id == LawyerOffer.lawyer_id)
            .where(Deal.id == deal_id)
            .limit(1)
        )
        row = (await self._session.execute(stmt)).first()
        if row is None:
            return None
        return int(row[0]), int(row[1])

    async def get_message(self, message_id: int) -> ChatMessage | None:
        return await self._session.get(ChatMessage, message_id)

    async def get_message_deal_id(self, message_id: int) -> int | None:
        stmt = select(ChatMessage.deal_id).where(ChatMessage.id == message_id).limit(1)
        return (await self._session.execute(stmt)).scalar_one_or_none()

    async def fetch_message_core_row(self, message_id: int) -> Row | None:
        stmt = (
            select(
                ChatMessage.id,
                ChatMessage.deal_id,
                func.coalesce(ChatMessage.client_id, UserRequest.client_id).label("client_id"),
                ChatMessage.sender_id,
                ChatMessage.text,
                ChatMessage.blocked_reason,
                ChatMessage.sent_at,
                ChatMessage.edited_at,
                ChatMessage.deleted_at,
            )
            .join(Deal, Deal.id == ChatMessage.deal_id)
            .join(UserRequest, UserRequest.id == Deal.request_id)
            .where(ChatMessage.id == message_id)
            .limit(1)
        )
        return (await self._session.execute(stmt)).first()

    async def count_messages_for_deal(self, deal_id: int, viewer_user_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(ChatMessage)
            .where(
                ChatMessage.deal_id == deal_id,
                _message_visible_to_viewer(viewer_user_id),
            )
        )
        return int((await self._session.execute(stmt)).scalar_one())

    async def fetch_messages_page_rows(
        self, deal_id: int, viewer_user_id: int, limit: int, offset: int
    ) -> Sequence[Row]:
        stmt = (
            select(
                ChatMessage.id,
                ChatMessage.deal_id,
                func.coalesce(ChatMessage.client_id, UserRequest.client_id).label("client_id"),
                ChatMessage.sender_id,
                ChatMessage.text,
                ChatMessage.blocked_reason,
                ChatMessage.sent_at,
                ChatMessage.edited_at,
                ChatMessage.deleted_at,
            )
            .join(Deal, Deal.id == ChatMessage.deal_id)
            .join(UserRequest, UserRequest.id == Deal.request_id)
            .where(
                ChatMessage.deal_id == deal_id,
                _message_visible_to_viewer(viewer_user_id),
            )
            .order_by(ChatMessage.sent_at.asc(), ChatMessage.id.asc())
            .offset(offset)
            .limit(limit)
        )
        return (await self._session.execute(stmt)).all()

    async def fetch_chats_list_rows(
        self, user_id: int, limit: int, offset: int
    ) -> Sequence[Row]:
        ClientUser = aliased(User)
        LawyerUser = aliased(User)
        LastMsg = aliased(ChatMessage)

        last_id_sq = (
            select(ChatMessage.id)
            .where(
                ChatMessage.deal_id == Deal.id,
                ChatMessage.deleted_at.is_(None),
                _message_visible_to_viewer(user_id),
            )
            .order_by(ChatMessage.sent_at.desc(), ChatMessage.id.desc())
            .limit(1)
            .correlate(Deal)
            .scalar_subquery()
        )

        stmt = (
            select(
                Deal.id.label("deal_id"),
                UserRequest.client_id,
                ClientUser.username.label("client_name"),
                LawyerProfile.user_id.label("lawyer_id"),
                LawyerUser.username.label("lawyer_name"),
                Deal.status.label("deal_status"),
                LastMsg.id.label("last_message_id"),
                LastMsg.text.label("last_message_text"),
                LastMsg.sender_id.label("last_message_sender_id"),
                LastMsg.sent_at.label("last_message_sent_at"),
            )
            .select_from(Deal)
            .join(UserRequest, UserRequest.id == Deal.request_id)
            .join(LawyerOffer, LawyerOffer.id == Deal.offer_id)
            .join(LawyerProfile, LawyerProfile.id == LawyerOffer.lawyer_id)
            .outerjoin(ClientUser, ClientUser.id == UserRequest.client_id)
            .outerjoin(LawyerUser, LawyerUser.id == LawyerProfile.user_id)
            .outerjoin(LastMsg, LastMsg.id == last_id_sq)
            .where(or_(UserRequest.client_id == user_id, LawyerProfile.user_id == user_id))
            .order_by(
                case((LastMsg.sent_at.is_(None), 1), else_=0).asc(),
                LastMsg.sent_at.desc().nulls_last(),
                Deal.id.desc(),
            )
            .limit(limit)
            .offset(offset)
        )
        return (await self._session.execute(stmt)).all()

    async def fetch_unread_counts_by_deals(
        self, deal_ids: list[int], reader_user_id: int
    ) -> dict[int, int]:
        if not deal_ids:
            return {}
        has_read = exists(
            select(1)
            .select_from(ChatMessageDeliveryStatus)
            .where(
                ChatMessageDeliveryStatus.message_id == ChatMessage.id,
                ChatMessageDeliveryStatus.user_id == reader_user_id,
                ChatMessageDeliveryStatus.status == ChatDeliveryStatus.READ,
            )
            .correlate(ChatMessage)
        )
        stmt = (
            select(ChatMessage.deal_id, func.count())
            .where(
                ChatMessage.deal_id.in_(deal_ids),
                ChatMessage.sender_id != reader_user_id,
                ChatMessage.deleted_at.is_(None),
                ~has_read,
            )
            .group_by(ChatMessage.deal_id)
        )
        rows = (await self._session.execute(stmt)).all()
        return {int(did): int(n) for did, n in rows}

    async def fetch_attachments_for_message_ids(
        self, message_ids: list[int]
    ) -> list[ChatAttachment]:
        if not message_ids:
            return []
        stmt = (
            select(ChatAttachment)
            .where(ChatAttachment.message_id.in_(message_ids))
            .order_by(ChatAttachment.message_id, ChatAttachment.id)
        )
        return list((await self._session.scalars(stmt)).all())

    async def fetch_edit_histories_for_message_ids(
        self, message_ids: list[int]
    ) -> list[ChatMessageEditHistory]:
        if not message_ids:
            return []
        stmt = (
            select(ChatMessageEditHistory)
            .where(ChatMessageEditHistory.message_id.in_(message_ids))
            .order_by(ChatMessageEditHistory.message_id, ChatMessageEditHistory.edited_at.desc())
        )
        return list((await self._session.scalars(stmt)).all())

    async def fetch_delivery_statuses_for_message_ids(
        self, message_ids: list[int]
    ) -> list[ChatMessageDeliveryStatus]:
        if not message_ids:
            return []
        stmt = (
            select(ChatMessageDeliveryStatus)
            .where(ChatMessageDeliveryStatus.message_id.in_(message_ids))
            .order_by(ChatMessageDeliveryStatus.message_id, ChatMessageDeliveryStatus.user_id)
        )
        return list((await self._session.scalars(stmt)).all())

    async def count_pending_attachments(
        self, ids: list[int], deal_id: int, uploaded_by_id: int
    ) -> int:
        stmt = select(func.count()).select_from(ChatAttachment).where(
            ChatAttachment.id.in_(ids),
            ChatAttachment.deal_id == deal_id,
            ChatAttachment.uploaded_by_id == uploaded_by_id,
            ChatAttachment.message_id.is_(None),
        )
        return int((await self._session.execute(stmt)).scalar_one())

    async def link_pending_attachments_to_message(
        self, ids: list[int], deal_id: int, uploaded_by_id: int, message_id: int
    ) -> None:
        await self._session.execute(
            update(ChatAttachment)
            .where(
                ChatAttachment.id.in_(ids),
                ChatAttachment.deal_id == deal_id,
                ChatAttachment.uploaded_by_id == uploaded_by_id,
                ChatAttachment.message_id.is_(None),
            )
            .values(message_id=message_id)
        )

    async def add_and_flush(self, *entities: object) -> None:
        for e in entities:
            self._session.add(e)
        await self._session.flush()

    async def add_delivery_status(self, row: ChatMessageDeliveryStatus) -> None:
        self._session.add(row)

    async def add_edit_history(self, row: ChatMessageEditHistory) -> None:
        self._session.add(row)

    async def get_delivery_status(
        self, message_id: int, user_id: int
    ) -> ChatMessageDeliveryStatus | None:
        stmt = select(ChatMessageDeliveryStatus).where(
            ChatMessageDeliveryStatus.message_id == message_id,
            ChatMessageDeliveryStatus.user_id == user_id,
        )
        return (await self._session.scalars(stmt)).first()

    async def apply_read_through_statuses(
        self,
        deal_id: int,
        reader_user_id: int,
        through_message_id: int,
        at: datetime,
    ) -> list[int]:
        stmt_ids = (
            select(ChatMessage.id)
            .where(
                ChatMessage.deal_id == deal_id,
                ChatMessage.id <= through_message_id,
                ChatMessage.sender_id != reader_user_id,
                ChatMessage.deleted_at.is_(None),
            )
            .order_by(ChatMessage.id)
        )
        ids = list((await self._session.scalars(stmt_ids)).all())
        if not ids:
            return []

        chunk_size = 500
        existing: dict[int, ChatMessageDeliveryStatus] = {}
        for i in range(0, len(ids), chunk_size):
            chunk = ids[i : i + chunk_size]
            stmt_ex = select(ChatMessageDeliveryStatus).where(
                ChatMessageDeliveryStatus.message_id.in_(chunk),
                ChatMessageDeliveryStatus.user_id == reader_user_id,
            )
            for row in (await self._session.scalars(stmt_ex)).all():
                existing[int(row.message_id)] = row

        affected: list[int] = []
        for mid in ids:
            row = existing.get(mid)
            if row is None:
                self._session.add(
                    ChatMessageDeliveryStatus(
                        message_id=mid,
                        user_id=reader_user_id,
                        status=ChatDeliveryStatus.READ,
                        at=at,
                    )
                )
                affected.append(mid)
            elif row.status != ChatDeliveryStatus.READ:
                row.status = ChatDeliveryStatus.READ
                row.at = at
                affected.append(mid)
        await self._session.flush()
        return affected

    async def mark_sent_as_delivered_in_deal(
        self,
        deal_id: int,
        recipient_user_id: int,
        at: datetime,
    ) -> list[int]:
        stmt = (
            select(ChatMessageDeliveryStatus)
            .join(ChatMessage, ChatMessage.id == ChatMessageDeliveryStatus.message_id)
            .where(
                ChatMessage.deal_id == deal_id,
                ChatMessageDeliveryStatus.user_id == recipient_user_id,
                ChatMessageDeliveryStatus.status == ChatDeliveryStatus.SENT,
                ChatMessage.sender_id != recipient_user_id,
                ChatMessage.deleted_at.is_(None),
            )
        )
        message_ids: list[int] = []
        for row in (await self._session.scalars(stmt)).all():
            row.status = ChatDeliveryStatus.DELIVERED
            row.at = at
            message_ids.append(int(row.message_id))
        if message_ids:
            await self._session.flush()
        return message_ids

    async def try_mark_message_delivered(
        self,
        message_id: int,
        recipient_user_id: int,
        at: datetime,
    ) -> bool:
        row = await self.get_delivery_status(message_id, recipient_user_id)
        if row is None or row.status != ChatDeliveryStatus.SENT:
            return False
        row.status = ChatDeliveryStatus.DELIVERED
        row.at = at
        await self._session.flush()
        return True
