from abc import ABC, abstractmethod
from typing import Optional

from pydantic import BaseModel


class ProductResult(BaseModel):
    """
    Normalized product data returned by every provider.
    This is the single shape the rest of the app works with,
    regardless of which provider fetched it.
    """

    external_id: str
    name: str
    price: float
    currency: str
    url: str
    image_url: Optional[str] = None
    source: str  # provider name: "mercadolibre" | "ebay" | "scraperapi"


class BaseProvider(ABC):
    """
    Interface that every provider must implement.
    Services depend only on this class, never on a concrete provider.
    """

    @abstractmethod
    async def search(self, query: str, limit: int = 5) -> list[ProductResult]:
        """Search products by keyword. Returns up to `limit` results."""
        pass

    @abstractmethod
    async def get_product(self, url: str) -> ProductResult:
        """Fetch current data for a specific product URL."""
        pass