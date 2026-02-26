from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.schemas import ProductWithPrices
from app import crud


router = APIRouter(
    prefix="/api/v1/products",
    tags=["Products API"]
)


def not_found_exception(message: str):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{message}"
    )


@router.get("/", response_model=list[ProductWithPrices], status_code=status.HTTP_200_OK)
async def get_products(db: AsyncSession = Depends(get_async_db)):
    return await crud.get_all_products(db)


@router.get("/{product_id}", response_model=ProductWithPrices, status_code=status.HTTP_200_OK)
async def get_product_by_id(product_id: int, db: AsyncSession = Depends(get_async_db)):
    product = await crud.get_product_by_id(product_id, db)
    if not product:
        not_found_exception("Product not found")
    return product


@router.delete("/all", status_code=status.HTTP_200_OK)
async def delete_all_products(db: AsyncSession = Depends(get_async_db)):
    await crud.delete_all_products(db)
    return {"message": "All products deleted"}


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product_by_id(product_id: int, db: AsyncSession = Depends(get_async_db)):
    is_deleted = await crud.delete_product_by_id(product_id, db)
    if not is_deleted:
        not_found_exception("Product not found")
    return {"message": f"Product ID:{product_id} deleted"}


@router.delete("/history/all", status_code=status.HTTP_200_OK)
async def delete_all_price_history(db: AsyncSession = Depends(get_async_db)):
    await crud.delete_all_price_history(db)
    return {"message": "All product price history has been deleted"}


@router.delete("/history/product/{product_id}", status_code=status.HTTP_200_OK)
async def delete_history_by_product_id(product_id: int, db: AsyncSession = Depends(get_async_db)):
    is_deleted = await crud.delete_history_by_product_id(product_id, db)
    if not is_deleted:
        not_found_exception("Product not found")
    return {"message": f"History of Product ID: {product_id} has been deleted"}


@router.delete("/history/{history_id}", status_code=status.HTTP_200_OK)
async def delete_history_by_history_id(history_id: int, db: AsyncSession = Depends(get_async_db)):
    history = await crud.delete_history_by_history_id(history_id, db)
    if not history:
        not_found_exception("History not found")
    return {"message": f"History ID: {history_id} has been deleted"}
