from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert

from app.database import async_session_maker
from app.models import Product, PriceHistory


async def save_parsed_data(parsed_items: list[dict]):
    """Gets list[dict] and save it to db (Upsert + Price History)"""
    async with async_session_maker() as session:
        for item in parsed_items:
            stmt = insert(Product).values(
                name=item["name"],
                url=item["url"],
                attributes=item["attributes"]
            )

            do_update_stmt = stmt.on_conflict_do_update(
                index_elements=["url"],
                set_=dict(
                    attributes=stmt.excluded.attributes,
                    updated_at=func.now()
                )
            ).returning(Product.id)

            result = await session.execute(do_update_stmt)
            product_id = result.scalar_one()

            new_price = PriceHistory(
                product_id=product_id,
                price=item["price"]
            )
            session.add(new_price)

        await session.commit()
