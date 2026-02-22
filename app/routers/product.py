from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.schemas import ProductWithPrices
from app import crud


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.get("/", response_model=list[ProductWithPrices])
async def get_products(db: AsyncSession = Depends(get_async_db)):
    return await crud.get_all_products(db)
