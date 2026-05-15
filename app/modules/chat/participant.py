"""Доступ к сделке для чата (SQLAlchemy 2.0)."""

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.deals.models import Deal
from app.modules.lawyer_profiles.models import LawyerProfile
from app.modules.offers.models import LawyerOffer
from app.modules.requests.models import UserRequest


async def deal_exists(session: AsyncSession, deal_id: int) -> bool:
    stmt = select(Deal.id).where(Deal.id == deal_id).limit(1)
    result = await session.execute(stmt)
    return result.scalar_one_or_none() is not None


async def is_deal_participant(session: AsyncSession, user_id: int, deal_id: int) -> bool:
    stmt = (
        select(Deal.id)
        .join(UserRequest, UserRequest.id == Deal.request_id)
        .join(LawyerOffer, LawyerOffer.id == Deal.offer_id)
        .join(LawyerProfile, LawyerProfile.id == LawyerOffer.lawyer_id)
        .where(
            Deal.id == deal_id,
            or_(UserRequest.client_id == user_id, LawyerProfile.user_id == user_id),
        )
        .limit(1)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none() is not None
