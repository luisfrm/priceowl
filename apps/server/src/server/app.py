from flask import Flask

from .config import settings
from .extensions import db, scheduler


def create_app() -> Flask:
    app = Flask(__name__)

    # --- config ---
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # --- extensions ---
    db.init_app(app)

    # --- database: create tables and seed ---
    with app.app_context():
        from .models.schema import Base, Provider, User, TrackedItem, ListProduct, PriceHistory

        Base.metadata.create_all(db.engine)

        from .seeds import seed_providers
        seed_providers()
        db.session.commit()

    # --- routes ---
    from .routes.product_routes import bp as product_bp
    from .routes.user_routes import bp as user_bp

    app.register_blueprint(product_bp, url_prefix="/api/products")
    app.register_blueprint(user_bp, url_prefix="/api/users")

    # --- scheduler ---
    try:
        from .jobs.daily_check import daily_price_check
        scheduler.add_job(
            func=daily_price_check,
            trigger="cron",
            hour=settings.DAILY_CHECK_HOUR,
            minute=settings.DAILY_CHECK_MINUTE,
            id="daily_price_check",
            replace_existing=True,
        )
        scheduler.start()
    except Exception:
        pass

    return app