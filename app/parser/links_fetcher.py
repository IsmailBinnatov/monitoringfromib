import aiohttp
from bs4 import BeautifulSoup

from app.logs.logger import logger


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


async def links_fetcher(url: str, session: aiohttp.ClientSession, offset: int = 0, limit: int = 10):
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

                limit = None if limit == 0 else offset + limit
                return links[offset: limit]
            else:
                logger.error(f"Parser: Error when requesting a page, status: {response.status} \n \
                             URL: {url}")
                return []
    except Exception as e:
        logger.error(f"Parser: Network error: {e}")
        return []
