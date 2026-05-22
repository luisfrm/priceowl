# PriceOwl — AGENTS.md

Price-tracking Telegram bot + Flask API. UV workspace monorepo. Most business-logic files are empty stubs; the app is not runnable out of the box.

## Monorepo boundaries

- `apps/bot/` — Telegram bot package. Handlers and `main.py` are empty stubs. Actual script entry point is `bot/__init__.py:main`.
- `apps/server/` — Flask API + scheduler. Only `app.py`, `config.py`, `extensions.py`, `schema.py`, and shared providers are implemented. Routes, services, repositories, and jobs are empty stubs.
- `packages/shared/` — Provider implementations (`ScraperAPIProvider`, `MercadoLibreProvider`, `EbayProvider`).

**`uv sync` quirk:** The root `pyproject.toml` has `dependencies = []` and does not depend on the workspace apps. `uv sync` alone only resolves the root package, so workspace members (and their deps like `httpx`) are **not installed** in `.venv`. Always run:

```bash
uv sync --all-packages
```

## Verified stack

- Python >=3.14 (all `pyproject.toml` files).
- `uv` workspace monorepo.
- `python-telegram-bot` >=22.7.
- Flask 3.x + Flask-SQLAlchemy + APScheduler.
- SQLAlchemy 2.x (modern `Mapped` / `mapped_column` style).
- Pydantic v2 + `pydantic-settings` for env validation.
- PostgreSQL only; no SQLite fallback.

## Entry points

- **Bot script:** `bot = "bot:main"` in `apps/bot/pyproject.toml` resolves to `apps/bot/src/bot/__init__.py:main`, **not** `main.py` (which is empty).
- **Server script:** `server = "server:main"` in `apps/server/pyproject.toml` resolves to `apps/server/src/server/__init__.py:main` (also a placeholder).
- **Flask app factory:** `create_app()` lives in `apps/server/src/server/app.py`.

**Runnable status:** `create_app()` is currently broken because it imports `bp` from empty route files (`product_routes.py`, `user_routes.py`) and `daily_price_check` from empty `daily_check.py`. The server will not start until those modules define the expected symbols.

## Database

- PostgreSQL only. URI is built inside `server.config.Settings.DATABASE_URL` from `POSTGRES_USER/PASSWORD/DB/HOST/PORT`.
- **No Alembic setup exists.** There is no `alembic.ini`, `migrations/`, or `versions/` directory. Do not attempt to run migrations.
- Schema lives in `apps/server/src/server/models/schema.py` (not `tables.py`). Models: `User`, `Provider`, `TrackedItem`, `ListProduct`, `PriceHistory`.
- `apps/server/src/server/seeds.py` is an incomplete stub meant to seed providers on startup (only `scraperapi` is active by default).
- Local Postgres: `docker compose up db`.

## Architecture rules (server)

Intended layered flow: Route → Service → Repository → Model. Enforce this when filling stubs:

- Routes never import repositories directly.
- Services never import Flask (`request`, `jsonify`, etc.).
- Repositories contain only SQLAlchemy queries; no business logic.
- Models are plain table definitions in `schema.py`.

## Provider contract

All providers extend `BaseProvider` in `packages/shared/`. The service layer must depend only on the abstract class.

```python
class BaseProvider(ABC):
    @abstractmethod
    async def search(self, query: str, limit: int = 5) -> list[ProductResult]: ...

    @abstractmethod
    async def get_product(self, url: str) -> ProductResult: ...
```

## Environment

Required variables (validated by Pydantic at startup; missing vars cause the app to fail):

```env
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
TELEGRAM_TOKEN=
```

Optional with defaults:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
FLASK_ENV=development
SECRET_KEY=change-me-in-production
DAILY_CHECK_HOUR=9
DAILY_CHECK_MINUTE=0
MERCADOLIBRE_CLIENT_ID=
MERCADOLIBRE_CLIENT_SECRET=
EBAY_APP_ID=
SCRAPERAPI_KEY=
```

Config is read from `.env` by `apps/server/src/server/config.py`.

## Extension instances

`apps/server/src/server/extensions.py` instantiates `db = SQLAlchemy()` and `scheduler = BackgroundScheduler()` at module level to avoid circular imports. They are bound to the Flask app inside `create_app()` via `db.init_app(app)` and `scheduler.start()`.

## Testing / linting / CI

None exist yet. There are no pytest, ruff, black, mypy, or GitHub Actions configs in the repo.
