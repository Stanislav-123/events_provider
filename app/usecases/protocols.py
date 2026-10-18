from datetime import date, datetime
from typing import Protocol
from uuid import UUID

from app.domain.entities import EventEntity, EventsPage, SyncMeta, TicketEntity


class EventsProviderClientProtocol(Protocol):
    async def get_seats(self, event_id: str | UUID) -> list[str]: ...

    async def register(
        self,
        event_id: str | UUID,
        first_name: str,
        last_name: str,
        email: str,
        seat: str,
    ) -> str: ...

    async def unregister(
        self,
        event_id: str | UUID,
        ticket_id: str | UUID,
    ) -> None: ...


class EventRepositoryProtocol(Protocol):
    async def get(self, event_id: UUID) -> EventEntity | None: ...

    async def list_page(
        self,
        *,
        date_from: date | None,
        page: int,
        page_size: int,
    ) -> EventsPage: ...

    async def upsert_from_provider(self, payload: dict) -> None: ...


class TicketRepositoryProtocol(Protocol):
    async def get(self, ticket_id: UUID) -> TicketEntity | None: ...

    async def create(
        self,
        *,
        ticket_id: UUID,
        event_id: UUID,
        first_name: str,
        last_name: str,
        email: str,
        seat: str,
    ) -> TicketEntity: ...

    async def delete(self, ticket_id: UUID) -> None: ...


class SyncStateRepositoryProtocol(Protocol):
    async def get(self) -> SyncMeta: ...

    async def mark_running(self) -> None: ...

    async def mark_success(
        self,
        *,
        sync_time: datetime,
        last_changed_at: datetime | None,
    ) -> None: ...

    async def mark_failed(self) -> None: ...


class SeatsCacheProtocol(Protocol):
    def get(self, event_id: str | UUID) -> list[str] | None: ...

    def set(self, event_id: str | UUID, seats: list[str]) -> None: ...
