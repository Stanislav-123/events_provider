from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.seats_cache import SeatsCache
from app.clients.events_provider import EventsProviderClient
from app.db.session import SessionFactory
from app.repositories.event import EventRepository
from app.repositories.sync_state import SyncStateRepository
from app.repositories.ticket import TicketRepository
from app.usecases.cancel_ticket import CancelTicketUsecase
from app.usecases.create_ticket import CreateTicketUsecase
from app.usecases.get_event import GetEventUsecase
from app.usecases.get_seats import GetSeatsUsecase
from app.usecases.list_events import ListEventsUsecase
from app.usecases.sync_events import SyncEventsUsecase


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_provider_client(request: Request) -> EventsProviderClient:
    return request.app.state.provider_client


def get_seats_cache(request: Request) -> SeatsCache:
    return request.app.state.seats_cache


def get_list_events_usecase(session: AsyncSession) -> ListEventsUsecase:
    return ListEventsUsecase(EventRepository(session))


def get_get_event_usecase(session: AsyncSession) -> GetEventUsecase:
    return GetEventUsecase(EventRepository(session))


def get_get_seats_usecase(
    session: AsyncSession,
    client: EventsProviderClient,
    cache: SeatsCache,
) -> GetSeatsUsecase:
    return GetSeatsUsecase(client, EventRepository(session), cache)


def get_create_ticket_usecase(
    session: AsyncSession,
    client: EventsProviderClient,
) -> CreateTicketUsecase:
    return CreateTicketUsecase(
        client,
        EventRepository(session),
        TicketRepository(session),
    )


def get_cancel_ticket_usecase(
    session: AsyncSession,
    client: EventsProviderClient,
) -> CancelTicketUsecase:
    return CancelTicketUsecase(client, TicketRepository(session))


def get_sync_events_usecase(
    session: AsyncSession,
    client: EventsProviderClient,
) -> SyncEventsUsecase:
    return SyncEventsUsecase(
        client,
        EventRepository(session),
        SyncStateRepository(session),
    )
