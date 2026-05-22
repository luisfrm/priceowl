# apps/server/src/server/seeds.py
from server.models.schema import Provider

def seed_providers():
    providers = [
        Provider(name="scraperapi", is_active=True),
        Provider(name="mercadolibre", is_active=False),
        Provider(name="ebay", is_active=False),
    ]