from server.extensions import db
from server.models.schema import Provider


def seed_providers() -> None:
    providers = [
        {"name": "scraperapi", "is_active": True},
        {"name": "mercadolibre", "is_active": False},
        {"name": "ebay", "is_active": False},
    ]
    for data in providers:
        existing = db.session.query(Provider).filter_by(name=data["name"]).first()
        if not existing:
            db.session.add(Provider(**data))
    db.session.commit()