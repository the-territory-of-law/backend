from pydantic import BaseModel, EmailStr

from app.modules.users.schemas import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthUserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    role: UserRole
