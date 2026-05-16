from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.requests.models import RequestStatusType as OrmRequestStatus
from app.modules.requests.models import UserRequest
from app.modules.requests.schemas import (
    RequestCategory,
    RequestStatusType,
    UserRequestCreate,
    UserRequestResponse,
    UserRequestUpdate,
)


class UserRequestRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user_request(
        self,
        request_data: UserRequestCreate,
        client_id: int,
    ) -> UserRequestResponse:
        user_request = UserRequest(
            client_id=client_id,
            **request_data.model_dump(),
        )
        self.session.add(user_request)
        await self.session.commit()
        await self.session.refresh(user_request)
        return UserRequestResponse.model_validate(user_request)

    async def get_by_id(self, request_id: int) -> UserRequest | None:
        return await self.session.get(UserRequest, request_id)

    async def list_requests(
        self,
        *,
        client_id: int | None = None,
        status: RequestStatusType | None = None,
        category: RequestCategory | None = None,
        budget_min: int | None = None,
        budget_max: int | None = None,
        limit: int,
        offset: int,
    ) -> tuple[list[UserRequest], int]:
        filters = []
        if client_id is not None:
            filters.append(UserRequest.client_id == client_id)
        if status is not None:
            filters.append(UserRequest.status == status.value)
        if category is not None:
            filters.append(UserRequest.category == category.value)
        if budget_min is not None:
            filters.append(UserRequest.budget_value >= budget_min)
        if budget_max is not None:
            filters.append(UserRequest.budget_value <= budget_max)

        count_stmt = select(func.count()).select_from(UserRequest)
        list_stmt = select(UserRequest)
        if filters:
            count_stmt = count_stmt.where(*filters)
            list_stmt = list_stmt.where(*filters)

        total = int((await self.session.execute(count_stmt)).scalar_one())
        list_stmt = (
            list_stmt.order_by(UserRequest.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(list_stmt)
        return list(result.scalars().all()), total

    async def update_user_request(
        self,
        request_id: int,
        data: UserRequestUpdate,
    ) -> UserRequest | None:
        user_request = await self.get_by_id(request_id)
        if user_request is None:
            return None

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(user_request, field, value)

        await self.session.commit()
        await self.session.refresh(user_request)
        return user_request

    async def close_user_request(self, request_id: int) -> UserRequest | None:
        user_request = await self.get_by_id(request_id)
        if user_request is None:
            return None
        user_request.status = OrmRequestStatus.CLOSED
        await self.session.commit()
        await self.session.refresh(user_request)
        return user_request
