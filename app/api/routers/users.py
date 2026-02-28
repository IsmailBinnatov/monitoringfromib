from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

import jwt

from app.models.models import User as UserModel, UserRole, RefreshToken
from app.schemas import UserCreate, UserRead, UserUpdate, RefreshTokenRequest
from app.database import get_async_db, settings

from app import exceptions

from app.auth.auth import create_access_token, create_refresh_token, is_super_admin, REFRESH_TOKEN_EXPIRE_DAYS
from app.auth.utils import verify_password, hash_password


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Registers a new user with the default role 'user'
    """
    user_email_exists = (await db.scalars(
        select(UserModel)
        .where(UserModel.email == user.email))
    ).first()

    if user_email_exists:
        exceptions.bad_request_exception("Email already registered")

    db_user = UserModel(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password)
    )

    db.add(db_user)
    await db.commit()
    return db_user


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_async_db)):
    """
    Authenticates the user and returns a JWT with id, username, role and email
    """
    user = (await db.scalars(
        select(UserModel)
        .where(UserModel.username == form_data.username))
    ).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        exceptions.credentials_exception_401("Incorrect email or password")

    user_data = {
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
        "role": user.role
    }
    access_token = create_access_token(data=user_data)
    refresh_token = create_refresh_token(data=user_data)

    refresh_token_expire_date = datetime.now(
        timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    db_refresh_token = RefreshToken(
        token=refresh_token,
        expires_at=refresh_token_expire_date.replace(tzinfo=None),
        user_id=user.id
    )

    db.add(db_refresh_token)
    await db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(body: RefreshTokenRequest, db: AsyncSession = Depends(get_async_db)):
    db_token = (await db.scalars(
        select(RefreshToken)
        .where(RefreshToken.token == body.refresh_token)
    )).first()

    if not db_token:
        exceptions.credentials_exception_401()

    await db.delete(db_token)
    await db.commit()

    return {"message": "Successful logout from the system"}


@router.post("/refresh-token", status_code=status.HTTP_200_OK)
async def refresh_token(body: RefreshTokenRequest, db: AsyncSession = Depends(get_async_db)):
    try:
        payload = jwt.decode(body.refresh_token, settings.SECRET_KEY,
                             algorithms=[settings.ALGORITHM])

        user_id_str = payload.get("sub")
        token_type = payload.get("token_type")

        if user_id_str is None or token_type != "refresh":
            exceptions.credentials_exception_401()

        user_id = int(user_id_str)

    except (jwt.ExpiredSignatureError, jwt.PyJWTError, ValueError):
        exceptions.credentials_exception_401()

    db_token = (await db.scalars(
        select(RefreshToken)
        .where(RefreshToken.token == body.refresh_token)
    )).first()

    user = (await db.scalars(
        select(UserModel)
        .where(UserModel.id == user_id, UserModel.is_active == True)
    )).first()

    if not db_token or not user:
        exceptions.credentials_exception_401()

    await db.delete(db_token)

    user_data = {
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
        "role": user.role
    }

    new_access_token = create_access_token(data=user_data)
    new_refresh_token = create_refresh_token(data=user_data)

    expire_date = datetime.now(timezone.utc) + \
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    new_db_token = RefreshToken(
        token=new_refresh_token,
        expires_at=expire_date.replace(tzinfo=None),
        user_id=user.id
    )

    db.add(new_db_token)
    await db.commit()

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.get("/", response_model=list[UserRead], status_code=status.HTTP_200_OK)
async def get_all_users(super_admin: UserModel = Depends(is_super_admin), db: AsyncSession = Depends(get_async_db)):
    """
    Returns all users (only for super-admin)
    """
    all_users = (await db.scalars(select(UserModel))).all()
    return all_users


@router.put("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def user_update(user_id: int, updated_user_data: UserUpdate, super_admin: UserModel = Depends(is_super_admin), db: AsyncSession = Depends(get_async_db)):
    """
    Update user only needed fields and returns updated user (only for super-admin)
    """
    user = (await db.scalars(
        select(UserModel)
        .where(UserModel.id == user_id))
    ).first()

    if not user:
        exceptions.not_found_exception_404("User")

    update_dict = updated_user_data.model_dump(exclude_unset=True)

    if not update_dict:
        exceptions.bad_request_exception_400("No data provided")

    stmt = update(UserModel).where(
        UserModel.id == user_id).values(**update_dict).returning(UserModel)
    updated_user = (await db.scalars(stmt)).first()
    await db.commit()

    return updated_user


@router.delete("/", status_code=status.HTTP_200_OK)
async def delete_non_super_admins(super_admin: UserModel = Depends(is_super_admin), db: AsyncSession = Depends(get_async_db)):
    """
    Deactives all non super-admins (only for super-admin)
    """
    await db.execute(
        update(UserModel).where(
            UserModel.role != UserRole.SUPER_ADMIN,
            UserModel.is_active == True
        ).values(is_active=False)
    )
    await db.commit()

    return {"message": "All non super-admins are deactivated."}


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_non_super_admins(user_id: int, super_admin: UserModel = Depends(is_super_admin), db: AsyncSession = Depends(get_async_db)):
    """
    Deactives non super-admin user (only for super-admin)
    """
    await db.execute(
        update(UserModel).where(
            UserModel.role != UserRole.SUPER_ADMIN,
            UserModel.id == user_id,
            UserModel.is_active == True
        ).values(is_active=False)
    )
    await db.commit()

    return {"message": f"User ID: {user_id} is deactivated."}
