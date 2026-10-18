import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import build_api_router
from app.cache.seats_cache import SeatsCache
from app.clients.events_provider import EventsProviderClient
from app.core.config import settings
from app.workers.sync_worker import SyncWorker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = EventsProviderClient(
        base_url=settings.events_provider_url,
        api_key=settings.events_provider_api_key,
    )
    await client.__aenter__()
    seats_cache = SeatsCache(ttl_seconds=settings.seats_cache_ttl_seconds)
    worker = SyncWorker(client)

    app.state.provider_client = client
    app.state.seats_cache = seats_cache
    app.state.sync_worker = worker

    if settings.enable_background_sync:
        try:
            worker.start()
        except Exception:
            logging.exception("Failed to start background sync worker")
    try:
        yield
    finally:
        if settings.enable_background_sync:
            try:
                await worker.stop()
            except Exception:
                logging.exception("Failed to stop background sync worker")
        await client.aclose()


def create_app() -> FastAPI:
    app = FastAPI(title="Events Aggregator", lifespan=lifespan)
    app.include_router(build_api_router())
    return app


app = create_app()
