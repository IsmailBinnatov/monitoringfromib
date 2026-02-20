import re
import aiohttp
from bs4 import BeautifulSoup


def in_stock_check(soup: BeautifulSoup) -> bool:
    div = soup.find("div", class_="nalich")
    if not div:
        return False

    status_text = div.text.strip()
    return status_text != "Нет в наличии"


def quick_find(pattern, text, group_no=0):
    match = re.search(pattern, text, re.I)
    return match.group(group_no).strip() if match else None


def get_product_attrs(title: str) -> dict:
    brand = quick_find(r"Смартфон\s+(\w+)", title, group_no=1)
    memory = quick_find(r"\d+(?:GB|TB)", title)
    sim = quick_find(r"(eSim|Dual[\s-]?Sim|Глобал|[\w-]*[\s-]?сим)", title)
    model = quick_find(
        rf"{brand}\s+(.*?)\s+{re.escape(memory)}", title, group_no=1)
    color = quick_find(rf"{re.escape(sim)}\s+(.*?)\s+\(", title, group_no=1)

    return {
        "brand": brand,
        "model": model,
        "memory": memory,
        "sim-version": sim,
        "color": color
    }


async def fetch_item_data(url: str, session: aiohttp.ClientSession):
    async with session.get(url=url) as response:
        html = await response.text()
        soup = BeautifulSoup(html, "lxml")

        in_stock = in_stock_check(soup)
        if not in_stock:
            print(f"Товара нет в наличии: {url}")
            return None

        product_full_name = soup.find("section", class_="main-content").find(
            "div", class_="row").find("h1").text

        offers = soup.find("div", {"itemprop": "offers"})
        if offers:
            price_tag = offers.find("span", class_="update_special") or \
                offers.find("span", class_="update_price")
            if price_tag:
                raw_price = price_tag.text.strip()
                price = int("".join(filter(str.isdigit, raw_price)))
            else:
                price = 0
        else:
            price = 0

    attrs = get_product_attrs(product_full_name)
    product_data = {
        "name": product_full_name,
        "price": price,
        "url": url,
        "attributes": attrs
    }
    print(f">>> Спарсили: {attrs['brand']} {attrs['model']} | Цена: {price}")

    return product_data


if __name__ == '__main__':
    import asyncio

    test_url_in_stock = "https://best-magazin.com/apple/iphone/iphone-17-air/iphone-17-air-512-gb-esim-black.html"
    test_url_not_in_stock = "https://best-magazin.com/apple/iphone/iphone-16-pro/iphone-16-pro-512gb-dual-sim-desert-titanium.html"

    async def test():
        async with aiohttp.ClientSession() as session:
            await fetch_item_data(url=test_url_in_stock, session=session)

    asyncio.run(test())
