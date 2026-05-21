# 🦉 PriceOwl — AGENTS.md

This file contains context, architecture decisions, and guidelines for AI agents (Cursor, Copilot, Claude, etc.) working on this codebase.

---

## Project Overview

**PriceOwl** is a price tracking monorepo built with Python and UV workspaces.
Users register products from multiple providers (MercadoLibre, eBay, ScraperAPI) via a Telegram bot,
and receive daily price summaries with delta tracking (price went up / down / unchanged).

### Apps
| App | Path | Description |
|-----|------|-------------|
| `bot` | `apps/bot/` | Telegram bot — user-facing interface, handles commands and conversations |
| `server` | `apps/server/` | Flask REST API — business logic, scheduling, DB access |

### Shared Package
| Package | Path | Description |
|---------|------|-------------|
| `shared` | `packages/shared/` | Providers, DTOs, base models, config — shared across apps |

---

## Tech Stack

| Layer | Library | Version | Notes |
|-------|---------|---------|-------|
| Package manager | `uv` | latest | Workspace monorepo |
| Bot framework | `python-telegram-bot` | v21 | Async native |
| Web framework | `Flask` | 3.x | App factory pattern |
| ORM | `SQLAlchemy` | 2.x | Modern style with type hints |
| Migrations | `Alembic` | latest | Run from `apps/server/` |
| Validation | `Pydantic` | v2 | DTOs, settings, provider contracts |
| Scheduler | `APScheduler` | 3.x | Cron jobs inside Flask process |
| HTTP client | `httpx` | latest | Async HTTP for provider calls |
| HTML parser | `BeautifulSoup4` | latest | Used by ScraperAPIProvider |
| DB (dev) | `SQLite` | — | Zero config local development |
| DB (prod) | `PostgreSQL` | 15+ | Via `psycopg2-binary` |

---

## Monorepo Structure

```
priceowl/
├── AGENTS.md                  # ← you are here
├── pyproject.toml             # UV workspace root
├── uv.lock
├── .env.example
├── .gitignore
│
├── apps/
│   ├── bot/
│   │   ├── pyproject.toml
│   │   └── src/bot/
│   │       ├── __init__.py
│   │       ├── main.py            # entry point, builds Application
│   │       └── handlers/
│   │           ├── __init__.py
│   │           ├── start.py       # /start command
│   │           ├── products.py    # /add, /list, /remove, /check
│   │           └── errors.py      # global error handler
│   │
│   └── server/
│       ├── pyproject.toml
│       └── src/server/
│           ├── __init__.py
│           ├── app.py             # Flask app factory: create_app()
│           ├── extensions.py      # db, scheduler instances (avoids circular imports)
│           ├── config.py          # Settings via Pydantic BaseSettings
│           │
│           ├── routes/
│           │   ├── __init__.py
│           │   ├── product_routes.py
│           │   └── user_routes.py
│           │
│           ├── services/
│           │   ├── __init__.py
│           │   ├── product_service.py        # business logic
│           │   ├── notification_service.py   # sends Telegram messages
│           │   └── provider_service.py       # resolves which provider to use
│           │
│           ├── repositories/
│           │   ├── __init__.py
│           │   ├── product_repository.py
│           │   ├── user_repository.py
│           │   └── provider_repository.py
│           │
│           ├── models/
│           │   ├── __init__.py
│           │   └── tables.py      # SQLAlchemy table definitions
│           │
│           └── jobs/
│               ├── __init__.py
│               └── daily_check.py # APScheduler job — runs every day at 9am
│
└── packages/
    └── shared/
        ├── pyproject.toml
        └── src/shared/
            ├── __init__.py
            ├── config.py              # Pydantic BaseSettings (reads .env)
            │
            └── providers/
                ├── __init__.py
                ├── base_provider.py           # ABC interface + ProductResult DTO
                ├── mercadolibre_provider.py   # Official MercadoLibre API
                ├── ebay_provider.py           # Official eBay Browse API
                └── scraperapi_provider.py     # ScraperAPI (Amazon scraping)
```

---

## Architecture — Server (Layered)

```
HTTP Request
    │
    ▼
[ Route / Blueprint ]   → only handles HTTP: parse request, return response
    │
    ▼
[ Service ]             → business logic, orchestration, NO direct DB access
    │
    ▼
[ Repository ]          → only data access: SQLAlchemy queries, no logic
    │
    ▼
[ SQLAlchemy Model ]    → table definition only, no methods
```

**Rules:**
- Routes never import repositories directly
- Services never import Flask (`request`, `jsonify`, etc.)
- Repositories never contain business logic
- Models are plain table definitions — no class methods with logic

---

## Database Models

```
User
├── telegram_id     PK  (integer, from Telegram)
├── username            (string, nullable)
└── created_at          (datetime, default now)

Provider
├── id              PK
├── name                ("mercadolibre" | "ebay" | "scraperapi")
├── is_active           (boolean, default true)
└── config              (JSON — API keys, base URLs, etc.)

Product
├── id              PK
├── user_id         FK → User.telegram_id
├── provider_id     FK → Provider.id
├── external_id         (product ID in the provider's system)
├── url
├── name
├── target_price        (optional — alert if price drops below this)
├── last_price
├── last_checked
└── created_at

PriceHistory
├── id              PK
├── product_id      FK → Product.id
├── price
└── checked_at
```

---

## Providers — Contract

Every provider must extend `BaseProvider` from `packages/shared`.
The service layer only depends on the base class — never on a concrete provider.

```python
# packages/shared/src/shared/providers/base_provider.py

class ProductResult(BaseModel):
    title: str
    price: float
    currency: str
    url: str
    image_url: str | None
    source: str   # provider name

class BaseProvider(ABC):
    @abstractmethod
    async def search(self, query: str) -> list[ProductResult]: ...

    @abstractmethod
    async def get_product(self, url: str) -> ProductResult: ...
```

---

## Telegram Bot — Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message + available commands menu |
| `/add <url>` | Register a product URL for daily tracking |
| `/list` | Show all tracked products with last known price |
| `/remove <id>` | Remove a product from tracking |
| `/check` | Force an immediate price check for all products |

---

## Daily Job

`apps/server/src/server/jobs/daily_check.py` runs every day at **9:00 AM (local server time)**.

Flow:
1. Fetch all users that have at least one tracked product
2. For each user, iterate their products
3. Call `provider.get_product(url)` for each product
4. Save new price to `PriceHistory`
5. Update `Product.last_price` and `Product.last_checked`
6. Call `notification_service.send_daily_summary(telegram_id, updates)`

---

## Environment Variables

All variables are defined in `.env` and validated at startup via Pydantic `BaseSettings`.
The app **will not start** if any required variable is missing.

```env
# Telegram
TELEGRAM_TOKEN=

# Database
DATABASE_URL=sqlite:///./priceowl.db   # dev
# DATABASE_URL=postgresql://user:pass@localhost:5432/priceowl  # prod

# Providers
MERCADOLIBRE_CLIENT_ID=
MERCADOLIBRE_CLIENT_SECRET=
EBAY_APP_ID=
SCRAPERAPI_KEY=
```

---

## Coding Conventions

- **Language:** Python 3.12+
- **Type hints:** mandatory on all function signatures
- **Docstrings:** on all public classes and methods
- **Async:** bot handlers and provider calls are `async def`; Flask routes are sync (Flask 3 handles threading)
- **Error handling:** raise domain exceptions from services; routes catch and return proper HTTP codes
- **Naming:**
  - Files: `snake_case`
  - Classes: `PascalCase`
  - Functions/variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`

---

## Local Development Setup

```bash
# 1. Clone and enter the project
git clone https://github.com/your-user/priceowl.git
cd priceowl

# 2. Install dependencies (UV handles the workspace)
uv sync

# 3. Copy and fill env variables
cp .env.example .env

# 4. Run DB migrations
cd apps/server
uv run alembic upgrade head

# 5. Start the server
uv run flask --app src/server/app.py run

# 6. Start the bot (separate terminal)
cd apps/bot
uv run python src/bot/main.py
```

---

## Git Conventions

```
feat:     new feature
fix:      bug fix
chore:    tooling, deps, config
refactor: code change with no behavior change
docs:     documentation only
```

Branch naming: `feat/add-ebay-provider`, `fix/daily-job-timezone`

---

*Last updated: 2026 — maintainer: your-user*