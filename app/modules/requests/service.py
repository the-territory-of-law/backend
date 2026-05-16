from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.requests.models import RequestStatusType as OrmRequestStatus
from app.modules.requests.models import UserRequest
from app.modules.requests.repository import UserRequestRepository
from app.modules.requests.schemas import (
    RequestCategory,
    RequestStatusType,
    UserRequestClose,
    UserRequestCreate,
    UserRequestResponse,
    UserRequestUpdate,
    UserRequestsPageResponse,
)
from app.modules.users.models import User
from app.modules.users.schemas import UserRole


def _can_view_request(user: User, user_request: UserRequest) -> bool:
    if user_request.client_id == user.id:
        return True
    if user.role == UserRole.ADMIN:
        return True
    if user.role == UserRole.LAWYER and user_request.status == OrmRequestStatus.OPEN:
        return True
    return False


def _require_client(user: User) -> None:
    if user.role != UserRole.CLIENT:
        raise HTTPException(status_code=403, detail="Only clients can perform this action")


def _require_owner(user: User, user_request: UserRequest) -> None:
    if user_request.client_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")


def _require_open(user_request: UserRequest) -> None:
    if user_request.status != OrmRequestStatus.OPEN:
        raise HTTPException(status_code=403, detail="Request is closed")


class UserRequestService:
    def __init__(self, session: AsyncSession):
        self.repo = UserRequestRepository(session)

    async def create(
        self, user: User, data: UserRequestCreate
    ) -> UserRequestResponse:
        _require_client(user)
        return await self.repo.create_user_request(data, client_id=user.id)

    async def get(self, user: User, request_id: int) -> UserRequestResponse:
        user_request = await self.repo.get_by_id(request_id)
        if user_request is None:
            raise HTTPException(status_code=404, detail="Request not found")
        if not _can_view_request(user, user_request):
            raise HTTPException(status_code=403, detail="Forbidden")
        return UserRequestResponse.model_validate(user_request)

    async def list(
        self,
        user: User,
        *,
        status: str | None,
        category: str | None,
        budget_min: int | None,
        budget_max: int | None,
        limit: int,
        offset: int,
    ) -> UserRequestsPageResponse:
        if budget_min is not None and budget_max is not None and budget_min > budget_max:
            raise HTTPException(status_code=400, detail="budget_min cannot exceed budget_max")

        status_filter: RequestStatusType | None = None
        if status is not None:
            try:
                status_filter = RequestStatusType(status)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail="Invalid status") from exc

        category_filter: RequestCategory | None = None
        if category is not None:
            try:
                category_filter = RequestCategory(category)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail="Invalid category") from exc

        client_id: int | None = None
        if user.role == UserRole.CLIENT:
            client_id = user.id

        items, total = await self.repo.list_requests(
            client_id=client_id,
            status=status_filter,
            category=category_filter,
            budget_min=budget_min,
            budget_max=budget_max,
            limit=limit,
            offset=offset,
        )
        return UserRequestsPageResponse(
            requests=[UserRequestResponse.model_validate(r) for r in items],
            total=total,
            has_more=offset + len(items) < total,
        )

    async def update(
        self, user: User, request_id: int, data: UserRequestUpdate
    ) -> UserRequestResponse:
        _require_client(user)
        user_request = await self.repo.get_by_id(request_id)
        if user_request is None:
            raise HTTPException(status_code=404, detail="Request not found")
        _require_owner(user, user_request)
        _require_open(user_request)

        updated = await self.repo.update_user_request(request_id, data)
        assert updated is not None
        return UserRequestResponse.model_validate(updated)

    async def close(
        self, user: User, request_id: int, _body: UserRequestClose
    ) -> UserRequestResponse:
        _require_client(user)
        user_request = await self.repo.get_by_id(request_id)
        if user_request is None:
            raise HTTPException(status_code=404, detail="Request not found")
        _require_owner(user, user_request)
        if user_request.status == OrmRequestStatus.CLOSED:
            raise HTTPException(status_code=400, detail="Request is already closed")

        closed = await self.repo.close_user_request(request_id)
        assert closed is not None
        return UserRequestResponse.model_validate(closed)
