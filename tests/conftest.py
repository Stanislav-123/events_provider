import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://events_user:local_dev_password@127.0.0.1:5432/events_db",
)
os.environ.setdefault("EVENTS_PROVIDER_URL", "https://events-provider.test")
os.environ.setdefault("EVENTS_PROVIDER_API_KEY", "test-api-key")
os.environ["ENABLE_BACKGROUND_SYNC"] = "false"
