from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert

from app.database import async_session_maker
from app.models import Product, PriceHistory


async def save_parsed_data(parsed_items: list[dict]):
    """Perform bulk upsert for products and record price history (only if changed)"""
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

        # UPSERT logic
        do_update_stmt = stmt.on_conflict_do_update(
            index_elements=["url"],
            set_=dict(
                attributes=stmt.excluded.attributes,
                updated_at=func.now()
            )
        ).returning(Product.id, Product.url)

        db_products = (await session.execute(do_update_stmt)).all()

        url_id_to_map = {row.url: row.id for row in db_products}
        product_ids = list(url_id_to_map.values())

        # Getting last prices from db
        latest_prices_stmt = (
            select(PriceHistory.product_id, PriceHistory.price)
            .distinct(PriceHistory.product_id)
            .where(PriceHistory.product_id.in_(product_ids))
            .order_by(PriceHistory.product_id, PriceHistory.created_at.desc())
        )

        latest_prices_result = (await session.execute(latest_prices_stmt)).all()
        last_price_map = {
            row.product_id: row.price for row in latest_prices_result}

        # Price comparison
        updated_prices_data = []
        for item in parsed_items:
            p_id = url_id_to_map[item["url"]]
            parsed_price = item["price"]

            last_db_price = last_price_map[p_id]

            if last_db_price != parsed_price:
                updated_prices_data.append(
                    PriceHistory(product_id=p_id, price=parsed_price)
                )

        if updated_prices_data:
            session.add_all(updated_prices_data)
            print(
                f"Price history updated for {len(updated_prices_data)} items.")
        else:
            print("Prices haven't changed. History hasn't been updated.")

        await session.commit()
