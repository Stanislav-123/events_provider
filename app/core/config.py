from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    events_provider_url: str
    events_provider_api_key: str
    sync_interval_seconds: int = 86_400
    seats_cache_ttl_seconds: int = 30
    enable_background_sync: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
