from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dependencies.dependencies import get_pagination_params
from app.common.dependencies.dependencies_schemas import PaginationParams
from app.core.database import get_db
from app.modules.users.schemas import UserUpdate
from repository import UserRepository
from schemas import UserCreate

router = APIRouter()

@router.post("/users")
async def create_user(
    user_data:  UserCreate,
    db: AsyncSession = Depends(get_db)
):
    repo = UserRepository(session=db)
    return await repo.create_user(user_data=user_data)


@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    repo = UserRepository(session=db)
    return await repo.get_user(user_id=user_id)


@router.get("/users")
async def get_all_users(
    pagination: PaginationParams = Depends(get_pagination_params),
    db: AsyncSession = Depends(get_db)
):
    repo = UserRepository(session=db)
    return await repo.get_users(limit=pagination.limit, offset=pagination.offset)


@router.patch("/users/{user_id}")
async def get_all_users(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    repo = UserRepository(session=db)
    return await repo.update_user(user_id=user_id, user_data=user_data)


@router.delete("/users/{user_id}")
async def get_all_users(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    repo = UserRepository(session=db)
    return await repo.delete_user(user_id=user_id)
