import asyncio
import aiohttp

from links_fetcher import links_fetcher
from item_parser import fetch_item_data


MAX_CONCURENT_REQUESTS = 2
URL_COUNT = 50
SITEMAP_URL = "https://best-magazin.com/ocsitemap.xml"


async def process_single_url(url: str, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore):
    async with semaphore:
        return await fetch_item_data(url=url, session=session)


async def main():
    """
    Main func that uses links_fetcher and fetch_item_data to complete the parser
    """
    semaphore = asyncio.Semaphore(MAX_CONCURENT_REQUESTS)

    async with aiohttp.ClientSession() as session:
        urls = await links_fetcher(url=SITEMAP_URL, session=session, limit=URL_COUNT)
        print(f"Найдено ссылок: {len(urls)}. Запускаем сбор данных...")

        tasks = [process_single_url(
            url=prod_url, session=session, semaphore=semaphore) for prod_url in urls]

        raw_results = await asyncio.gather(*tasks)
    valid_data = [item for item in raw_results if item is not None]

    print("-----------------------------------")
    print(valid_data)
    return valid_data


if __name__ == '__main__':
    final_data = asyncio.run(main())
