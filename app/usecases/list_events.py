from datetime import date

from app.domain.entities import EventsPage
from app.usecases.protocols import EventRepositoryProtocol


class ListEventsUsecase:
    def __init__(self, events: EventRepositoryProtocol) -> None:
        self._events = events

    async def do(
        self,
        *,
        date_from: date | None,
        page: int,
        page_size: int,
    ) -> EventsPage:
        return await self._events.list_page(
            date_from=date_from,
            page=page,
            page_size=page_size,
        )
