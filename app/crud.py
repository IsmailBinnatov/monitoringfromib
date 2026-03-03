from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import delete, select, func

from app.models import Product, PriceHistory
from app import exceptions


# ----- Product and Price


async def get_all_products(
        page: int,
        page_size: int,
        min_price: int | None,
        max_price: int | None,
        db: AsyncSession
):
    if min_price is not None and max_price is not None and min_price > max_price:
        exceptions.bad_request_exception_400(
            "min_price cannot be greater than max_price")

    subquery = (
        select(func.max(PriceHistory.id))
        .group_by(PriceHistory.product_id)
        .scalar_subquery()
    )
    stmt = (
        select(Product)
        .join(PriceHistory)
        .filter(PriceHistory.id.in_(subquery))
        .options(selectinload(Product.prices))
    )

    if min_price is not None:
        stmt = stmt.filter(PriceHistory.price >= min_price)
    if max_price is not None:
        stmt = stmt.filter(PriceHistory.price <= max_price)

    total_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(total_stmt) or 0

    final_stmt = (
        stmt.order_by(Product.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    products = (await db.scalars(final_stmt)).unique().all()

    return {
        "products": products,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


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
