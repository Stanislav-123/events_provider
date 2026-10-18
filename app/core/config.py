from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _to_asyncpg_url(url: str) -> str:
    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url.removeprefix("postgres://")
    if url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url.removeprefix("postgresql://")
    return url


class Settings(BaseSettings):
    database_url: str = Field(alias="DATABASE_URL")
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

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: object) -> object:
        if isinstance(value, str):
            return _to_asyncpg_url(value.strip())
        return value

    @field_validator("events_provider_url", mode="before")
    @classmethod
    def normalize_provider_url(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().rstrip("/")
        return value


settings = Settings()
