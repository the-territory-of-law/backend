from fastapi import APIRouter, Depends, Response, Request, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.database import get_db
from app.common.dependencies.dependencies import get_current_user
from app.core.security import (
    TOKEN_TYPE_REFRESH,
    set_auth_cookies,
    clear_auth_cookies,
    create_access_token,
)
from app.modules.users.models import User
from app.modules.users.schemas import UserCreate
from .service import AuthService

settings = Settings()

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(user_data: UserCreate, response: Response, db: AsyncSession = Depends(get_db)):
    user = await AuthService.register(db, user_data)
    set_auth_cookies(response, user.id)
    return {"message": "Registered successfully", "user": user}


@router.post("/login")
async def login(
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    user = await AuthService.authenticate(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    set_auth_cookies(response, user.id)
    return {"message": "Logged in successfully"}


@router.post("/refresh")
async def refresh_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    refresh_token = request.cookies.get(settings.COOKIE_REFRESH_NAME)
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")

    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != TOKEN_TYPE_REFRESH:
            raise HTTPException(status_code=401)

        user_id = payload.get("sub")
        user = await db.get(User, int(user_id))
        if not user:
            raise HTTPException(status_code=401)

        # Выдаём новый access токен
        new_access = create_access_token({"sub": str(user.id)})
        response.set_cookie(
            key=settings.COOKIE_NAME,
            value=new_access,
            httponly=settings.COOKIE_HTTPONLY,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            domain=settings.COOKIE_DOMAIN,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        return {"message": "Token refreshed"}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.post("/logout")
async def logout(
    response: Response,
    _user: User = Depends(get_current_user),
):
    clear_auth_cookies(response)
    return {"message": "Logged out"}
