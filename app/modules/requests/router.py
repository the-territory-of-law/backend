from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dependencies.dependencies import get_current_user, get_pagination_params
from app.common.dependencies.dependencies_schemas import PaginationParams
from app.core.database import get_db
from app.modules.requests.schemas import (
    UserRequestClose,
    UserRequestCreate,
    UserRequestResponse,
    UserRequestUpdate,
    UserRequestsPageResponse,
)
from app.modules.requests.service import UserRequestService
from app.modules.users.models import User

router = APIRouter(prefix="/requests", tags=["requests"])


@router.post("", response_model=UserRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_request(
    body: UserRequestCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserRequestService(db)
    return await service.create(user, body)


@router.get("", response_model=UserRequestsPageResponse)
async def list_requests(
    user: User = Depends(get_current_user),
    pagination: PaginationParams = Depends(get_pagination_params),
    db: AsyncSession = Depends(get_db),
    status: str | None = None,
    category: str | None = None,
    budget_min: int | None = None,
    budget_max: int | None = None,
):
    service = UserRequestService(db)
    return await service.list(
        user,
        status=status,
        category=category,
        budget_min=budget_min,
        budget_max=budget_max,
        limit=pagination.limit,
        offset=pagination.offset,
    )


@router.get("/{request_id}", response_model=UserRequestResponse)
async def get_request(
    request_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserRequestService(db)
    return await service.get(user, request_id)


@router.patch("/{request_id}", response_model=UserRequestResponse)
async def update_request(
    request_id: int,
    body: UserRequestUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserRequestService(db)
    return await service.update(user, request_id, body)


@router.post("/{request_id}/close", response_model=UserRequestResponse)
async def close_request(
    request_id: int,
    body: UserRequestClose,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserRequestService(db)
    return await service.close(user, request_id, body)
