from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- Flask ---
    FLASK_ENV: str = "development"
    SECRET_KEY: str = "change-me-in-production"

    # --- Environment ---
    APP_ENV: str = "local"

    # --- Database ---
    DATABASE_URL: str | None = None
    SQLITE_DATABASE_URL: str = "sqlite:///priceowl.db"

    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str | None = None
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL

        if self.APP_ENV in ("local", "development", ""):
            return self.SQLITE_DATABASE_URL

        if not all([self.POSTGRES_USER, self.POSTGRES_PASSWORD, self.POSTGRES_DB]):
            raise ValueError(
                "POSTGRES_USER, POSTGRES_PASSWORD, and POSTGRES_DB are required "
                f"when APP_ENV='{self.APP_ENV}'"
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

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()