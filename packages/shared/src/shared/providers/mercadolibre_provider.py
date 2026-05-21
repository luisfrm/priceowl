import httpx

from .base_provider import BaseProvider, ProductResult


ML_BASE = "https://api.mercadolibre.com"


class MercadoLibreProvider(BaseProvider):
    """
    Fetches product data via the official MercadoLibre API.
    Requires a client_id and client_secret from developers.mercadolibre.com.

    NOTE: is_active=False in the database until credentials are configured.
    """

    def __init__(self, client_id: str, client_secret: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token: str | None = None

    async def _get_access_token(self) -> str:
        """Fetch an access token using client credentials flow."""
        if self._access_token:
            return self._access_token

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ML_BASE}/oauth/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            )
            response.raise_for_status()
            self._access_token = response.json()["access_token"]
            return self._access_token

    async def search(self, query: str, limit: int = 5) -> list[ProductResult]:
        token = await self._get_access_token()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ML_BASE}/sites/MLA/search",
                params={"q": query, "limit": limit},
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()

        items = response.json().get("results", [])
        results: list[ProductResult] = []

        for item in items[:limit]:
            try:
                results.append(
                    ProductResult(
                        external_id=item["id"],
                        name=item["title"],
                        price=float(item["price"]),
                        currency=item["currency_id"],
                        url=item["permalink"],
                        image_url=item.get("thumbnail"),
                        source="mercadolibre",
                    )
                )
            except (KeyError, ValueError):
                continue

        return results

    async def get_product(self, url: str) -> ProductResult:
        """
        Extract the item ID from the URL and fetch current data from the API.
        MercadoLibre URLs follow the pattern: .../MLA-XXXXXXXXX-...
        """
        token = await self._get_access_token()

        # Extract item ID from URL: MLA123456789
        import re
        match = re.search(r"(MLA-?\d+)", url.upper())
        if not match:
            raise ValueError(f"Could not extract MercadoLibre item ID from URL: {url}")

        item_id = match.group(1).replace("-", "")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ML_BASE}/items/{item_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()

        item = response.json()

        return ProductResult(
            external_id=item["id"],
            name=item["title"],
            price=float(item["price"]),
            currency=item["currency_id"],
            url=item["permalink"],
            image_url=item.get("thumbnail"),
            source="mercadolibre",
        )