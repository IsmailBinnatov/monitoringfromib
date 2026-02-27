from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
import jwt

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.database import get_async_db
from app.models.models import User as UserModel


ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")


def credentials_exception(message: str = "Could not validate credentials"):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"{message}",
        headers={"WWW-Authenticate": "Bearer"}
    )


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
            credentials_exception("Token payload missing 'sub'")

        try:
            user_id = int(sub)
        except ValueError:
            credentials_exception("Invalid user ID format")

        if user_id <= 0:
            credentials_exception("Invalid user ID format")

    except jwt.ExpiredSignatureError:
        credentials_exception("Token has expired")
    except jwt.PyJWTError:
        credentials_exception()

    user = (await db.scalars(
        select(UserModel)
        .where(UserModel.id == user_id, UserModel.is_active == True))
    ).first()

    if not user:
        credentials_exception()

    return user
