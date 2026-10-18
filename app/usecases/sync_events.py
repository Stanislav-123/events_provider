import logging
from datetime import datetime, timezone
from typing import Protocol

from app.clients.paginator import EventsPaginator
from app.domain.exceptions import SyncAlreadyRunning
from app.usecases.protocols import (
    EventRepositoryProtocol,
    SyncStateRepositoryProtocol,
)

logger = logging.getLogger(__name__)

FIRST_SYNC_CHANGED_AT = "2000-01-01"


class EventsPageClient(Protocol):
    async def get_events(
        self,
        changed_at: str,
        cursor_url: str | None = None,
    ) -> dict: ...


class SyncEventsUsecase:
    def __init__(
        self,
        client: EventsPageClient,
        events: EventRepositoryProtocol,
        sync_state: SyncStateRepositoryProtocol,
    ) -> None:
        self._client = client
        self._events = events
        self._sync_state = sync_state

    async def do(self) -> dict:
        meta = await self._sync_state.get()
        if meta.sync_status == "running":
            raise SyncAlreadyRunning

        changed_at = (
            meta.last_changed_at.date().isoformat()
            if meta.last_changed_at is not None
            else FIRST_SYNC_CHANGED_AT
        )

        await self._sync_state.mark_running()
        logger.info("Starting events sync with changed_at=%s", changed_at)

        max_changed_at = meta.last_changed_at
        processed = 0

        try:
            async for event_payload in EventsPaginator(
                self._client,
                changed_at=changed_at,
            ):
                await self._events.upsert_from_provider(event_payload)
                processed += 1

                event_changed_at = datetime.fromisoformat(
                    event_payload["changed_at"]
                )
                if max_changed_at is None or event_changed_at > max_changed_at:
                    max_changed_at = event_changed_at

            await self._sync_state.mark_success(
                sync_time=datetime.now(timezone.utc),
                last_changed_at=max_changed_at,
            )
            logger.info("Events sync finished, processed=%s", processed)
            return {
                "processed": processed,
                "last_changed_at": (
                    max_changed_at.isoformat() if max_changed_at else None
                ),
                "status": "success",
            }
        except Exception:
            logger.exception("Events sync failed")
            await self._sync_state.mark_failed()
            raise
