from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import TicketEntity
from app.models.ticket import Ticket
from app.repositories.mappers import ticket_to_entity


class TicketRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, ticket_id: UUID) -> TicketEntity | None:
        ticket = await self._session.get(Ticket, ticket_id)
        if ticket is None:
            return None
        return ticket_to_entity(ticket)

    async def create(
        self,
        *,
        ticket_id: UUID,
        event_id: UUID,
        first_name: str,
        last_name: str,
        email: str,
        seat: str,
    ) -> TicketEntity:
        ticket = Ticket(
            id=ticket_id,
            event_id=event_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat,
        )
        self._session.add(ticket)
        await self._session.flush()
        return ticket_to_entity(ticket)

    async def delete(self, ticket_id: UUID) -> None:
        ticket = await self._session.get(Ticket, ticket_id)
        if ticket is not None:
            await self._session.delete(ticket)
