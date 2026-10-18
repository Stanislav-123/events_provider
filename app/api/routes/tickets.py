from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    get_cancel_ticket_usecase,
    get_create_ticket_usecase,
    get_provider_client,
    get_session,
)
from app.api.provider_errors import http_exception_from_provider
from app.api.schemas.tickets import (
    CancelTicketResponse,
    CreateTicketRequest,
    CreateTicketResponse,
)
from app.clients.events_provider import EventsProviderClient
from app.domain.exceptions import (
    EventNotFound,
    EventUnexpectedStatus,
    ProviderError,
    TicketNotFound,
)
from app.usecases.cancel_ticket import CancelTicketUsecase
from app.usecases.create_ticket import CreateTicketUsecase

router = APIRouter(tags=["tickets"])


@router.post(
    "/api/tickets/",
    response_model=CreateTicketResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=True,
)
@router.post(
    "/api/tickets",
    response_model=CreateTicketResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def create_ticket(
    body: CreateTicketRequest,
    session: AsyncSession = Depends(get_session),
    client: EventsProviderClient = Depends(get_provider_client),
) -> CreateTicketResponse:
    usecase: CreateTicketUsecase = get_create_ticket_usecase(session, client)
    try:
        ticket_id = await usecase.do(
            event_id=body.event_id,
            first_name=body.first_name,
            last_name=body.last_name,
            email=str(body.email),
            seat=body.seat,
        )
    except EventNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        ) from exc
    except EventUnexpectedStatus as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except ProviderError as exc:
        raise http_exception_from_provider(exc) from exc

    return CreateTicketResponse(ticket_id=ticket_id)


@router.delete(
    "/api/tickets/{ticket_id}/",
    response_model=CancelTicketResponse,
    include_in_schema=True,
)
@router.delete(
    "/api/tickets/{ticket_id}",
    response_model=CancelTicketResponse,
    include_in_schema=False,
)
async def cancel_ticket(
    ticket_id: UUID,
    session: AsyncSession = Depends(get_session),
    client: EventsProviderClient = Depends(get_provider_client),
) -> CancelTicketResponse:
    usecase: CancelTicketUsecase = get_cancel_ticket_usecase(session, client)
    try:
        await usecase.do(ticket_id)
    except TicketNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        ) from exc
    except ProviderError as exc:
        raise http_exception_from_provider(exc) from exc

    return CancelTicketResponse(success=True)
