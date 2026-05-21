# apps/server/src/server/seeds.py
def seed_providers():
    providers = [
        Provider(name="scraperapi", is_active=True),
        Provider(name="mercadolibre", is_active=False),
        Provider(name="ebay", is_active=False),
    ]