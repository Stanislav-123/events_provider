from uuid import UUID

from app.domain.entities import EventEntity
from app.domain.exceptions import EventNotFound
from app.usecases.protocols import EventRepositoryProtocol


class GetEventUsecase:
    def __init__(self, events: EventRepositoryProtocol) -> None:
        self._events = events

    async def do(self, event_id: UUID) -> EventEntity:
        event = await self._events.get(event_id)
        if event is None:
            raise EventNotFound
        return event
