from fastapi import Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dependencies.dependencies_schemas import PaginationParams
from app.core.database import get_db
from app.core.security import get_current_user_from_cookie
from app.modules.users.models import User


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    return await get_current_user_from_cookie(request, db)


def get_pagination_params(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
) -> PaginationParams:
    return PaginationParams(
        limit=size,
        offset=(page - 1) * size
    )