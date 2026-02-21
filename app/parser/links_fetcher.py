import aiohttp
from bs4 import BeautifulSoup


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


async def links_fetcher(url: str, session: aiohttp.ClientSession, limit: int = 10):
    """
    Makes 1 request to the donor-site sitemap
    """
    try:
        async with session.get(url=url, headers=headers) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, "xml")

                locs = soup.find_all("loc")
                links = [
                    loc.text for loc in locs if "/apple/iphone/" in loc.text and loc.text.endswith(".html")]

                return links[:limit]
            else:
                print(f"Ошибка сервера: {response.status}")
                return []
    except Exception as e:
        print(f"Ошибка сети: {e}")
        return []


if __name__ == "__main__":
    import asyncio

    SITEMAP_URL = "https://best-magazin.com/ocsitemap.xml"

    async def test():
        async with aiohttp.ClientSession() as session:
            print(f"--- Тестовый запуск ---")
            links = await links_fetcher(SITEMAP_URL, session)
            print(f"Найдено ссылок: {len(links)}")
            for l in links:
                print(l)

    asyncio.run(test())
