from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app import crud


router = APIRouter(
    prefix="/products",
    tags=["Website: Products"]
)
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def get_products(request: Request, db: AsyncSession = Depends(get_async_db)):
    products = await crud.get_all_products(db)
    return templates.TemplateResponse(
        name="index.html",
        context={
            "request": request,
            "products": products
        }
    )


@router.get("/{product_id}")
async def get_product_by_id(request: Request, product_id: int, db: AsyncSession = Depends(get_async_db)):
    product = await crud.get_product_by_id(product_id, db)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return templates.TemplateResponse(
        name="product_detail.html",
        context={
            "request": request,
            "product": product
        }
    )
