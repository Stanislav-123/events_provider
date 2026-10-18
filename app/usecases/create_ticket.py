from uuid import UUID

from app.domain.entities import EventStatus
from app.domain.exceptions import EventNotFound, EventUnexpectedStatus
from app.usecases.protocols import (
    EventRepositoryProtocol,
    EventsProviderClientProtocol,
    TicketRepositoryProtocol,
)


class CreateTicketUsecase:
    def __init__(
        self,
        client: EventsProviderClientProtocol,
        events: EventRepositoryProtocol,
        tickets: TicketRepositoryProtocol,
    ) -> None:
        self._client = client
        self._events = events
        self._tickets = tickets

    async def do(
        self,
        *,
        event_id: UUID,
        first_name: str,
        last_name: str,
        email: str,
        seat: str,
    ) -> UUID:
        event = await self._events.get(event_id)
        if event is None:
            raise EventNotFound

        if event.status != EventStatus.published:
            raise EventUnexpectedStatus(
                f"Event status must be published, got {event.status}"
            )

        ticket_id = await self._client.register(
            event.id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat,
        )
        await self._tickets.create(
            ticket_id=UUID(str(ticket_id)),
            event_id=event.id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat,
        )
        return UUID(str(ticket_id))
