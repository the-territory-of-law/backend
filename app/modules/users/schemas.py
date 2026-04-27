from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserRole(StrEnum):
    ADMIN = "admin"
    LAWYER = "lawyer"
    CLIENT = "client"


class UserBase(BaseModel):
    name: str
    password: str
    role: UserRole
    email: str


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str]
    password: Optional[str]
    role: Optional[UserRole]
    email: Optional[str]


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    role: UserRole
