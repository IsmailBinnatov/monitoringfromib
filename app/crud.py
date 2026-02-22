from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.models import Product


async def get_all_products(db: AsyncSession):
    products = (await db.scalars(select(Product).options(selectinload(Product.prices)))).all()
    return products
