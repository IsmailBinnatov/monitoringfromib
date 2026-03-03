from typing import Optional
from fastapi import APIRouter, Depends, Query, Request, HTTPException, status
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
async def get_products(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=50),
    min_price: Optional[str] = Query(None),
    max_price: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_db)
):
    def clean_price(p):
        if p is not None and p.strip().isdigit():
            return int(p)
        return None

    clean_min = clean_price(min_price)
    clean_max = clean_price(max_price)

    pagination_data = await crud.get_all_products(page=page, page_size=page_size, min_price=clean_min, max_price=clean_max, db=db)
    return templates.TemplateResponse(
        name="index.html",
        context={
            "request": request,
            "products": pagination_data
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
