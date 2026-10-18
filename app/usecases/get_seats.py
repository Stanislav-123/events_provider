from uuid import UUID

from app.domain.exceptions import EventNotFound
from app.usecases.protocols import (
    EventRepositoryProtocol,
    EventsProviderClientProtocol,
    SeatsCacheProtocol,
)


class GetSeatsUsecase:
    def __init__(
        self,
        client: EventsProviderClientProtocol,
        events: EventRepositoryProtocol,
        cache: SeatsCacheProtocol,
    ) -> None:
        self._client = client
        self._events = events
        self._cache = cache

    async def do(self, event_id: UUID) -> list[str]:
        event = await self._events.get(event_id)
        if event is None:
            raise EventNotFound

        cached = self._cache.get(event_id)
        if cached is not None:
            return cached

        seats = await self._client.get_seats(event_id)
        self._cache.set(event_id, seats)
        return seats
