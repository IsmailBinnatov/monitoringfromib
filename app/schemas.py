from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class ProductRead(BaseModel):
    id: int
    name: str
    url: str
    attributes: dict
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PriceRead(BaseModel):
    id: int
    price: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductWithPrices(ProductRead):
    prices: list[PriceRead] = []
