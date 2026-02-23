from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.schemas import ProductWithPrices
from app import crud


router = APIRouter(
    prefix="/api/v1/products",
    tags=["Products API"]
)


@router.get("/", response_model=list[ProductWithPrices], status_code=status.HTTP_200_OK)
async def get_products(db: AsyncSession = Depends(get_async_db)):
    return await crud.get_all_products(db)


@router.get("/{product_id}", response_model=ProductWithPrices, status_code=status.HTTP_200_OK)
async def get_product_by_id(product_id: int, db: AsyncSession = Depends(get_async_db)):
    return await crud.get_product_by_id(product_id, db)
