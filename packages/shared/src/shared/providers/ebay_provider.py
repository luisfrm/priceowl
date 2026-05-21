import httpx

from .base_provider import BaseProvider, ProductResult


EBAY_BASE = "https://api.ebay.com"


class EbayProvider(BaseProvider):
    """
    Fetches product data via the official eBay Browse API.
    Requires an App ID (client_id) from developer.ebay.com.

    NOTE: is_active=False in the database until credentials are configured.
    """

    def __init__(self, app_id: str) -> None:
        self.app_id = app_id
        self._access_token: str | None = None

    async def _get_access_token(self) -> str:
        """Fetch an OAuth application token."""
        if self._access_token:
            return self._access_token

        import base64
        credentials = base64.b64encode(f"{self.app_id}:".encode()).decode()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{EBAY_BASE}/identity/v1/oauth2/token",
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={
                    "grant_type": "client_credentials",
                    "scope": "https://api.ebay.com/oauth/api_scope",
                },
            )
            response.raise_for_status()
            self._access_token = response.json()["access_token"]
            return self._access_token

    async def search(self, query: str, limit: int = 5) -> list[ProductResult]:
        token = await self._get_access_token()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{EBAY_BASE}/buy/browse/v1/item_summary/search",
                params={"q": query, "limit": limit},
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()

        items = response.json().get("itemSummaries", [])
        results: list[ProductResult] = []

        for item in items[:limit]:
            try:
                price_data = item.get("price", {})
                results.append(
                    ProductResult(
                        external_id=item["itemId"],
                        name=item["title"],
                        price=float(price_data.get("value", 0)),
                        currency=price_data.get("currency", "USD"),
                        url=item["itemWebUrl"],
                        image_url=item.get("image", {}).get("imageUrl"),
                        source="ebay",
                    )
                )
            except (KeyError, ValueError):
                continue

        return results

    async def get_product(self, url: str) -> ProductResult:
        """
        Extract the item ID from the URL and fetch via eBay Browse API.
        eBay URLs follow the pattern: .../itm/XXXXXXXXX
        """
        token = await self._get_access_token()

        import re
        match = re.search(r"/itm/(\d+)", url)
        if not match:
            raise ValueError(f"Could not extract eBay item ID from URL: {url}")

        item_id = match.group(1)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{EBAY_BASE}/buy/browse/v1/item/v1|{item_id}|0",
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()

        item = response.json()
        price_data = item.get("price", {})

        return ProductResult(
            external_id=item["itemId"],
            name=item["title"],
            price=float(price_data.get("value", 0)),
            currency=price_data.get("currency", "USD"),
            url=item["itemWebUrl"],
            image_url=item.get("image", {}).get("imageUrl"),
            source="ebay",
        )