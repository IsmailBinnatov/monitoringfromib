from pydantic import BaseModel, EmailStr, ConfigDict, field_serializer
from datetime import datetime


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
