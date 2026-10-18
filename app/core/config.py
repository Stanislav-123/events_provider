
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    postgres_host: str = Field(alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_username: str = Field(alias="POSTGRES_USERNAME")
    postgres_password: str = Field(alias="POSTGRES_PASSWORD")
    postgres_database_name: str = Field(alias="POSTGRES_DATABASE_NAME")

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
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.postgres_username,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_database_name,
        ).render_as_string(hide_password=False)

    @field_validator("events_provider_url", mode="before")
    @classmethod
    def normalize_provider_url(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().rstrip("/")
        return value


settings = Settings()
