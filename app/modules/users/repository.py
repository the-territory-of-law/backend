from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.security import hash_password
from app.modules.users.models import User
from app.modules.users.schemas import UserCreate, UserResponse, UserUpdate


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        hashed_password = hash_password(user_data.password)
        user = User(
            username=user_data.name,
            hashed_password=hashed_password,
            email=user_data.email,
            role=user_data.role,
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            role=user.role
        )

    async def get_users(self, limit: int, offset: int) -> List[UserResponse]:
        request = select(User).limit(limit).offset(offset)
        result = await self.session.execute(request)
        users = result.scalars().all()
        return [
            UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                role=user.role
            )
            for user in users
        ]

    async def get_user(self, user_id: int) -> UserResponse:
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalars().one()
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            role=user.role
        )

    async def get_user_model(self, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def update_user(self, user_id: int, user_data: UserUpdate) -> UserResponse:
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalars().one()

        update_data = user_data.model_dump(exclude_unset=True)

        if "name" in update_data:
            user.username = update_data["name"]
        if "email" in update_data:
            user.email = update_data["email"]
        if "role" in update_data:
            user.role = update_data["role"]
        if "password" in update_data:
            user.hashed_password = hash_password(update_data["password"])

        await self.session.commit()
        await self.session.refresh(user)

        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            role=user.role
        )

    async def delete_user(self, user_id: int) -> bool:
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalars().one()

        await self.session.delete(user)
        await self.session.commit()
        return True
    