from uuid import UUID

from app.domain.exceptions import TicketNotFound
from app.usecases.protocols import (
    EventsProviderClientProtocol,
    TicketRepositoryProtocol,
)


class CancelTicketUsecase:
    def __init__(
        self,
        client: EventsProviderClientProtocol,
        tickets: TicketRepositoryProtocol,
    ) -> None:
        self._client = client
        self._tickets = tickets

    async def do(self, ticket_id: UUID) -> None:
        ticket = await self._tickets.get(ticket_id)
        if ticket is None:
            raise TicketNotFound

        await self._client.unregister(ticket.event_id, ticket.ticket_id)
        await self._tickets.delete(ticket.ticket_id)
