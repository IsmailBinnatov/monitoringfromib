from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.schemas import ProductWithPrices
from app import crud

from app import exceptions

from app.models.models import User as UserModel
from app.auth.auth import is_admin, is_super_admin


router = APIRouter(
    prefix="/api/v1/products",
    tags=["Products API"]
)


# ----- Method: GET


@router.get("/", response_model=list[ProductWithPrices], status_code=status.HTTP_200_OK)
async def get_products(db: AsyncSession = Depends(get_async_db)):
    """Returns all products"""
    return await crud.get_all_products(db)


@router.get("/{product_id}", response_model=ProductWithPrices, status_code=status.HTTP_200_OK)
async def get_product_by_id(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """Returns product foundend by id"""
    product = await crud.get_product_by_id(product_id, db)
    if not product:
        exceptions.not_found_exception_404("Product")
    return product


# ----- Method: DELETE


@router.delete("/all", status_code=status.HTTP_200_OK)
async def delete_all_products(super_admin: UserModel = Depends(is_super_admin), db: AsyncSession = Depends(get_async_db)):
    """Delete all products (Hard Delete) (only for super-admin)"""
    await crud.delete_all_products(db)
    return {"message": "All products has been deleted"}


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product_by_id(product_id: int, admin: UserModel = Depends(is_admin), db: AsyncSession = Depends(get_async_db)):
    """Delete product by id (only for admin and super-admin)"""
    is_deleted = await crud.delete_product_by_id(product_id, db)
    if not is_deleted:
        exceptions.not_found_exception_404("Product")
    return {"message": f"Product ID:{product_id} has been deleted"}


@router.delete("/history/all", status_code=status.HTTP_200_OK)
async def delete_all_price_history(super_admin: UserModel = Depends(is_super_admin), db: AsyncSession = Depends(get_async_db)):
    """Clear all price history (Hard Delete) (only for super-admin)"""
    await crud.delete_all_price_history(db)
    return {"message": "All product price history has been deleted"}


@router.delete("/history/product/{product_id}", status_code=status.HTTP_200_OK)
async def delete_history_by_product_id(product_id: int, admin: UserModel = Depends(is_admin), db: AsyncSession = Depends(get_async_db)):
    """Delete history by product id (only for admin and super-admin)"""
    is_deleted = await crud.delete_history_by_product_id(product_id, db)
    if not is_deleted:
        exceptions.not_found_exception_404("Product")
    return {"message": f"History of Product ID: {product_id} has been deleted"}


@router.delete("/history/{history_id}", status_code=status.HTTP_200_OK)
async def delete_history_by_history_id(history_id: int, admin: UserModel = Depends(is_admin), db: AsyncSession = Depends(get_async_db)):
    """Delete history by id (only for admin and super-admin)"""
    history = await crud.delete_history_by_history_id(history_id, db)
    if not history:
        exceptions.not_found_exception_404("History")
    return {"message": f"History ID: {history_id} has been deleted"}
