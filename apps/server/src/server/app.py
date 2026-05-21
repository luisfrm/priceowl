from flask import Flask

from .config import settings
from .extensions import db, scheduler
from .jobs.daily_check import daily_price_check


def create_app() -> Flask:
    app = Flask(__name__)

    # --- config ---
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # --- extensions ---
    db.init_app(app)

    # --- routes ---
    from .routes.product_routes import bp as product_bp
    from .routes.user_routes import bp as user_bp

    app.register_blueprint(product_bp, url_prefix="/api/products")
    app.register_blueprint(user_bp, url_prefix="/api/users")

    # --- scheduler ---
    scheduler.add_job(
        func=daily_price_check,
        trigger="cron",
        hour=settings.DAILY_CHECK_HOUR,
        minute=settings.DAILY_CHECK_MINUTE,
        id="daily_price_check",
        replace_existing=True,
    )
    scheduler.start()

    return app