import click
from flask import Flask

from .config import settings
from .extensions import db, migrate


def create_app() -> Flask:
    app = Flask(__name__)

    # --- config ---
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # --- extensions ---
    db.init_app(app)
    
    # Import Base to register models in metadata and configure Migrate to use it
    from .models.schema import Base
    migrate.init_app(app, db, metadata=Base.metadata)

    # --- cli commands ---
    @app.cli.command("seed-db")
    def seed_db():
        """Seeds the database with initial providers."""
        from .seeds import seed_providers
        seed_providers()
        click.echo("Database seeded successfully.")

    # --- routes ---
    from .routes.product_routes import bp as product_bp
    from .routes.user_routes import bp as user_bp

    app.register_blueprint(product_bp, url_prefix="/api/products")
    app.register_blueprint(user_bp, url_prefix="/api/users")

    return app