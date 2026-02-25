from pydantic import BaseModel, EmailStr, ConfigDict, field_serializer, Field
from datetime import datetime

from app.models.models import UserRole


# ----- Product and Price


class PriceRead(BaseModel):
    id: int
    price: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('created_at')
    def format_datetime(self, dt: datetime, _info):
        return dt.strftime("%H:%M:%S, %d.%m.%y")


class ProductRead(BaseModel):
    id: int
    name: str
    url: str
    attributes: dict
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('created_at', 'updated_at')
    def format_datetime(self, dt: datetime, _info):
        return dt.strftime("%H:%M:%S, %d.%m.%y")


class ProductWithPrices(ProductRead):
    prices: list[PriceRead] = []


# ----- User


class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=20)
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=4, max_length=20)


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=2, max_length=20)
    email: EmailStr | None = Field(default=None)
    password: str | None = Field(default=None, min_length=4, max_length=20)
    role: UserRole | None = Field(default=None)
