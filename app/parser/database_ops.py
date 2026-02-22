from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert

from app.database import async_session_maker
from app.models import Product, PriceHistory


async def save_parsed_data(parsed_items: list[dict]):
    """Perform bulk upsert for products and record price history"""
    if not parsed_items:
        return

    async with async_session_maker() as session:
        products_data = [
            {
                "name": item["name"],
                "url": item["url"],
                "attributes": item["attributes"]
            }
            for item in parsed_items
        ]

        stmt = insert(Product).values(products_data)

        do_update_stmt = stmt.on_conflict_do_update(
            index_elements=["url"],
            set_=dict(
                attributes=stmt.excluded.attributes,
                updated_at=func.now()
            )
        ).returning(Product.id, Product.url)

        result = await session.execute(do_update_stmt)
        db_products = result.all()

        url_id_to_map = {row.url: row.id for row in db_products}

        prices_data = [
            PriceHistory(
                product_id=url_id_to_map[item["url"]],
                price=item["price"]
            )
            for item in parsed_items
        ]

        session.add_all(prices_data)
        await session.commit()
