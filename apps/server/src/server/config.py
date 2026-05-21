from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- Flask ---
    FLASK_ENV: str = "development"
    SECRET_KEY: str = "change-me-in-production"

    # --- Database ---
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    @property
    def DATABASE_URL(self) -> str:
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