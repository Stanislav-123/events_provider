
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


def _to_asyncpg_url(url: str) -> str:
    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url.removeprefix("postgres://")
    if url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url.removeprefix("postgresql://")
    return url


class Settings(BaseSettings):
    database_url_override: str | None = Field(
        default=None,
        alias="DATABASE_URL",
    )

    postgres_host: str | None = Field(
        default=None,
        alias="POSTGRES_HOST",
    )
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_username: str | None = Field(
        default=None,
        alias="POSTGRES_USERNAME",
    )
    postgres_password: str | None = Field(
        default=None,
        alias="POSTGRES_PASSWORD",
    )
    postgres_database_name: str | None = Field(
        default=None,
        alias="POSTGRES_DATABASE_NAME",
    )

    events_provider_url: str = Field(alias="EVENTS_PROVIDER_URL")
    events_provider_api_key: str = Field(alias="EVENTS_PROVIDER_API_KEY")

    sync_interval_seconds: int = 86_400
    seats_cache_ttl_seconds: int = 30
    enable_background_sync: bool = True
    port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    @property
    def database_url(self) -> str:
        if self.database_url_override:
            return _to_asyncpg_url(self.database_url_override.strip())

        postgres_parts = (
            self.postgres_host,
            self.postgres_username,
            self.postgres_password,
            self.postgres_database_name,
        )

        if all(value is not None for value in postgres_parts):
            return URL.create(
                drivername="postgresql+asyncpg",
                username=self.postgres_username,
                password=self.postgres_password,
                host=self.postgres_host,
                port=self.postgres_port,
                database=self.postgres_database_name,
            ).render_as_string(hide_password=False)

        # Fallback for test collection and local health-only tests.
        # Real database operations require valid connection settings.
        return "postgresql+asyncpg://postgres:postgres@localhost:5432/events_db"

    @field_validator("events_provider_url", mode="before")
    @classmethod
    def normalize_provider_url(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().rstrip("/")
        return value


settings = Settings()
