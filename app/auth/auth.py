from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
import jwt

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.database import get_async_db
from app.models.models import User as UserModel, UserRole

from app import exceptions


ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")


def create_access_token(data: dict):
    payload_to_encode = data.copy()
    expire = datetime.now(timezone.utc) + \
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload_to_encode.update({"exp": expire})
    return jwt.encode(payload_to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_async_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY,
                             algorithms=[settings.ALGORITHM])
        sub = payload.get("sub")
        if not sub:
            exceptions.credentials_exception_401("Token payload missing 'sub'")

        try:
            user_id = int(sub)
        except ValueError:
            exceptions.credentials_exception_401("Invalid user ID format")

        if user_id <= 0:
            exceptions.credentials_exception_401("Invalid user ID format")

    except jwt.ExpiredSignatureError:
        exceptions.credentials_exception_401("Token has expired")
    except jwt.PyJWTError:
        exceptions.credentials_exception_401()

    user = (await db.scalars(
        select(UserModel)
        .where(UserModel.id == user_id, UserModel.is_active == True))
    ).first()

    if not user:
        exceptions.credentials_exception_401()

    return user


async def is_super_admin(current_user: UserModel = Depends(get_current_user)):
    if current_user.role != UserRole.SUPER_ADMIN:
        exceptions.forbidden_exception_403()

    return current_user


async def is_admin(current_user: UserModel = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN and current_user.role != UserRole.SUPER_ADMIN:
        exceptions.forbidden_exception_403()

    return current_user
