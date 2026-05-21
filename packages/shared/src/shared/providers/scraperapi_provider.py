import httpx
from bs4 import BeautifulSoup

from .base_provider import BaseProvider, ProductResult


SCRAPERAPI_BASE = "http://api.scraperapi.com"


class ScraperAPIProvider(BaseProvider):
    """
    Fetches Amazon product data via ScraperAPI.
    ScraperAPI handles proxies, captchas, and headless rendering — we just
    send the target URL and get back the rendered HTML.
    """

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def _build_url(self, target_url: str) -> str:
        """Wrap a target URL with the ScraperAPI endpoint."""
        return f"{SCRAPERAPI_BASE}?api_key={self.api_key}&url={target_url}"

    async def search(self, query: str, limit: int = 5) -> list[ProductResult]:
        """
        Search Amazon for products matching `query`.
        Scrapes the search results page and returns up to `limit` items.
        """
        encoded_query = query.replace(" ", "+")
        amazon_search_url = f"https://www.amazon.com/s?k={encoded_query}"

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(self._build_url(amazon_search_url))
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results: list[ProductResult] = []

        # Each product card on Amazon search has this data-component-type attribute
        cards = soup.select("[data-component-type='s-search-result']")

        for card in cards[:limit]:
            try:
                asin = card.get("data-asin", "")
                name_tag = card.select_one("h2 span")
                price_whole = card.select_one(".a-price-whole")
                price_fraction = card.select_one(".a-price-fraction")
                image_tag = card.select_one("img.s-image")

                if not asin or not name_tag or not price_whole:
                    continue

                price_str = price_whole.text.strip().replace(",", "")
                fraction_str = price_fraction.text.strip() if price_fraction else "00"
                price = float(f"{price_str}{fraction_str}")

                results.append(
                    ProductResult(
                        external_id=asin,
                        name=name_tag.text.strip(),
                        price=price,
                        currency="USD",
                        url=f"https://www.amazon.com/dp/{asin}",
                        image_url=image_tag["src"] if image_tag else None,
                        source="scraperapi",
                    )
                )
            except (ValueError, TypeError):
                # skip malformed cards silently
                continue

        return results

    async def get_product(self, url: str) -> ProductResult:
        """
        Fetch current price and data for a specific Amazon product URL.
        """
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(self._build_url(url))
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        asin_tag = soup.find("input", {"id": "ASIN"})
        asin = asin_tag["value"] if asin_tag else url.split("/dp/")[-1].split("/")[0]

        name_tag = soup.select_one("#productTitle")
        price_tag = soup.select_one(".a-price .a-offscreen")
        image_tag = soup.select_one("#landingImage")

        if not name_tag or not price_tag:
            raise ValueError(f"Could not parse product data from URL: {url}")

        price_str = price_tag.text.strip().replace("$", "").replace(",", "")

        return ProductResult(
            external_id=asin,
            name=name_tag.text.strip(),
            price=float(price_str),
            currency="USD",
            url=url,
            image_url=image_tag["src"] if image_tag else None,
            source="scraperapi",
        )