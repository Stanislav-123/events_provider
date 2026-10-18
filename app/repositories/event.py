from datetime import date, datetime, time, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities import EventEntity, EventsPage
from app.models.event import Event
from app.models.place import Place
from app.repositories.mappers import event_to_entity


class EventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, event_id: UUID) -> EventEntity | None:
        event = await self._session.get(
            Event,
            event_id,
            options=(selectinload(Event.place),),
        )
        if event is None:
            return None
        return event_to_entity(event, include_seats_pattern=True)

    async def list_page(
        self,
        *,
        date_from: date | None,
        page: int,
        page_size: int,
    ) -> EventsPage:
        filters = []
        if date_from is not None:
            start = datetime.combine(date_from, time.min, tzinfo=timezone.utc)
            filters.append(Event.event_time >= start)

        count_stmt = select(func.count()).select_from(Event)
        if filters:
            count_stmt = count_stmt.where(*filters)
        total = int(await self._session.scalar(count_stmt) or 0)

        stmt = (
            select(Event)
            .options(selectinload(Event.place))
            .order_by(Event.event_time.asc(), Event.id.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        if filters:
            stmt = stmt.where(*filters)

        result = await self._session.scalars(stmt)
        events = [
            event_to_entity(event, include_seats_pattern=False)
            for event in result.all()
        ]
        return EventsPage(
            count=total,
            page=page,
            page_size=page_size,
            results=events,
        )

    async def upsert_from_provider(self, payload: dict) -> None:
        place_data = payload["place"]
        place = await self._session.get(Place, UUID(str(place_data["id"])))
        if place is None:
            place = Place(id=UUID(str(place_data["id"])))
            self._session.add(place)

        place.name = place_data["name"]
        place.city = place_data["city"]
        place.address = place_data["address"]
        place.seats_pattern = place_data["seats_pattern"]
        place.created_at = _parse_dt(place_data["created_at"])
        place.changed_at = _parse_dt(place_data["changed_at"])

        event_id = UUID(str(payload["id"]))
        event = await self._session.get(Event, event_id)
        if event is None:
            event = Event(id=event_id)
            self._session.add(event)

        event.place_id = place.id
        event.name = payload["name"]
        event.event_time = _parse_dt(payload["event_time"])
        event.registration_deadline = _parse_dt(payload["registration_deadline"])
        event.status = payload["status"]
        event.number_of_visitors = int(payload["number_of_visitors"])
        event.created_at = _parse_dt(payload["created_at"])
        event.changed_at = _parse_dt(payload["changed_at"])
        event.status_changed_at = _parse_dt(payload["status_changed_at"])


def _parse_dt(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)
