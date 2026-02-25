import asyncio
import aiohttp

from app.parser.links_fetcher import links_fetcher
from app.parser.item_parser import fetch_item_data
from app.parser.database_ops import save_parsed_data


MAX_CONCURENT_REQUESTS = 2
OFFSET = 0  # last value 50
URL_COUNT = 50
SITEMAP_URL = "https://best-magazin.com/ocsitemap.xml"


async def process_single_url(url: str, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore):
    async with semaphore:
        return await fetch_item_data(url=url, session=session)


async def main():
    """
    Main func that uses links_fetcher, fetch_item_data and save_parsed_data to complete the parser
    """
    semaphore = asyncio.Semaphore(MAX_CONCURENT_REQUESTS)

    async with aiohttp.ClientSession() as session:
        urls = await links_fetcher(url=SITEMAP_URL, session=session, offset=OFFSET, limit=URL_COUNT)
        print(f"Найдено ссылок: {len(urls)}. Запускаем сбор данных...")

        tasks = [process_single_url(
            url=prod_url, session=session, semaphore=semaphore) for prod_url in urls]

        raw_results = await asyncio.gather(*tasks)
    valid_data = [item for item in raw_results if item is not None]

    if valid_data:
        print(
            f"--- Сбор окончен. Сохраняем {len(valid_data)} товаров в БД ---")
        await save_parsed_data(valid_data)
        print(f"--- Данные успешно сохранены: {len(valid_data)} шт. ---")

    print("-----------------------------------")
    print(valid_data)
    return valid_data


if __name__ == '__main__':
    final_data = asyncio.run(main())
