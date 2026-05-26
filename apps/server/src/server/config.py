from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Flask ---
    FLASK_ENV: str = "development"
    SECRET_KEY: str = "change-me-in-production"

    # --- Environment ---
    APP_ENV: str = "local"

    # --- Database ---
    DATABASE_URL: str | None = None

    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str | None = None
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL

        if not all([self.POSTGRES_USER, self.POSTGRES_PASSWORD, self.POSTGRES_DB]):
            raise ValueError(
                "POSTGRES_USER, POSTGRES_PASSWORD, and POSTGRES_DB are required. "
                "Please configure them in your .env file or run PostgreSQL locally (e.g. docker compose up db)."
            )

        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # --- Telegram ---
    TELEGRAM_TOKEN: str

    # --- Providers ---
    MERCADOLIBRE_CLIENT_ID: str = ""
    MERCADOLIBRE_CLIENT_SECRET: str = ""
    EBAY_APP_ID: str = ""
    SCRAPERAPI_KEY: str = ""

    # --- Scheduler ---
    DAILY_CHECK_HOUR: int = 9
    DAILY_CHECK_MINUTE: int = 0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()