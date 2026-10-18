import asyncio
import logging

from app.clients.events_provider import EventsProviderClient
from app.core.config import settings
from app.db.session import SessionFactory
from app.repositories.event import EventRepository
from app.repositories.sync_state import SyncStateRepository
from app.usecases.sync_events import SyncEventsUsecase

logger = logging.getLogger(__name__)


class SyncWorker:
    def __init__(
        self,
        client: EventsProviderClient,
        interval_seconds: int | None = None,
    ) -> None:
        self._client = client
        self._interval_seconds = (
            interval_seconds
            if interval_seconds is not None
            else settings.sync_interval_seconds
        )
        self._task: asyncio.Task | None = None
        self._stop_event = asyncio.Event()

    def start(self) -> None:
        if self._task is None or self._task.done():
            self._stop_event.clear()
            self._task = asyncio.create_task(self._run_loop())

    async def stop(self) -> None:
        self._stop_event.set()
        if self._task is not None:
            await self._task
            self._task = None

    async def _run_loop(self) -> None:
        logger.info(
            "Background sync worker started, interval=%ss",
            self._interval_seconds,
        )
        await self._reset_stale_running_status()
        while not self._stop_event.is_set():
            try:
                await self._run_once()
            except Exception:
                logger.exception("Background sync iteration failed")

            try:
                await asyncio.wait_for(
                    self._stop_event.wait(),
                    timeout=self._interval_seconds,
                )
            except TimeoutError:
                continue

    async def _reset_stale_running_status(self) -> None:
        async with SessionFactory() as session:
            sync_state = SyncStateRepository(session)
            meta = await sync_state.get()
            if meta.sync_status == "running":
                await sync_state.mark_failed()
                logger.warning("Reset stale sync_status=running to failed")

    async def _run_once(self) -> None:
        async with SessionFactory() as session:
            usecase = SyncEventsUsecase(
                self._client,
                EventRepository(session),
                SyncStateRepository(session),
            )
            try:
                await usecase.do()
                await session.commit()
            except Exception:
                await session.rollback()
                raise
