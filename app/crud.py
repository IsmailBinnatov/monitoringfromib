from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import delete, select

from app.models import Product, PriceHistory


async def get_all_products(db: AsyncSession):
    products = (await db.scalars(select(Product).options(selectinload(Product.prices)))).all()
    return products


async def get_product_by_id(product_id: int, db: AsyncSession):
    product = (await db.scalars(
        select(Product)
        .options(selectinload(Product.prices))
        .where(Product.id == product_id))
    ).first()
    return product


async def delete_all_products(db: AsyncSession):
    await db.execute(delete(Product))
    await db.commit()


async def delete_product_by_id(product_id: int, db: AsyncSession):
    product = await get_product_by_id(product_id, db)
    if product:
        await db.delete(product)
        await db.commit()
        return True
    return False


async def delete_all_price_history(db: AsyncSession):
    await db.execute(delete(PriceHistory))
    await db.commit()


async def delete_history_by_product_id(product_id: int, db: AsyncSession):
    product = await db.get(Product, product_id)
    if not product:
        return False
    stmt = delete(PriceHistory).where(PriceHistory.product_id == product_id)
    await db.execute(stmt)
    await db.commit()
    return True


async def delete_history_by_history_id(history_id: int, db: AsyncSession):
    price_history = (await db.scalars(
        select(PriceHistory)
        .where(PriceHistory.id == history_id))
    ).first()

    if price_history:
        await db.delete(price_history)
        await db.commit()
        return True
    return False
