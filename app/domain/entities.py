from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum
from uuid import UUID


class EventStatus(StrEnum):
    new = "new"
    draft = "draft"
    published = "published"
    registration_closed = "registration_closed"
    finished = "finished"
    cancelled = "cancelled"


@dataclass(frozen=True, slots=True)
class PlaceEntity:
    id: UUID
    name: str
    city: str
    address: str
    seats_pattern: str | None = None


@dataclass(frozen=True, slots=True)
class EventEntity:
    id: UUID
    name: str
    place: PlaceEntity
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int


@dataclass(frozen=True, slots=True)
class EventsPage:
    count: int
    page: int
    page_size: int
    results: list[EventEntity]


@dataclass(frozen=True, slots=True)
class TicketEntity:
    ticket_id: UUID
    event_id: UUID
    first_name: str
    last_name: str
    email: str
    seat: str


@dataclass(frozen=True, slots=True)
class SyncMeta:
    last_sync_time: datetime | None
    last_changed_at: datetime | None
    sync_status: str


@dataclass(frozen=True, slots=True)
class ListEventsQuery:
    date_from: date | None
    page: int
    page_size: int
