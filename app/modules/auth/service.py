from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserCreate, UserResponse


class AuthService:
    @staticmethod
    async def register(db: AsyncSession, user_data: UserCreate) -> UserResponse:
        repo = UserRepository(session=db)
        existing_user = await repo.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )
        return await repo.create_user(user_data=user_data)

    @staticmethod
    async def authenticate(db: AsyncSession, email: str, password: str):
        repo = UserRepository(session=db)
        user = await repo.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
