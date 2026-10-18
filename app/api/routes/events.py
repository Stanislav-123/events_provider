from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    get_get_event_usecase,
    get_get_seats_usecase,
    get_list_events_usecase,
    get_provider_client,
    get_seats_cache,
    get_session,
)
from app.api.pagination import build_page_link
from app.api.schemas.events import (
    EventDetailSchema,
    EventListItemSchema,
    EventsListResponse,
    PlaceDetailSchema,
    PlaceListSchema,
    SeatsResponse,
)
from app.cache.seats_cache import SeatsCache
from app.clients.events_provider import EventsProviderClient
from app.domain.exceptions import EventNotFound, ProviderError
from app.usecases.get_event import GetEventUsecase
from app.usecases.get_seats import GetSeatsUsecase

router = APIRouter(tags=["events"])


@router.get("/api/events/", response_model=EventsListResponse, name="list_events")
async def list_events(
    request: Request,
    date_from: date | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> EventsListResponse:
    usecase = get_list_events_usecase(session)
    result = await usecase.do(
        date_from=date_from,
        page=page,
        page_size=page_size,
    )

    next_link = None
    if page * page_size < result.count:
        next_link = build_page_link(
            request,
            page=page + 1,
            page_size=page_size,
            date_from=date_from,
            total=result.count,
        )

    previous_link = None
    if page > 1:
        previous_link = build_page_link(
            request,
            page=page - 1,
            page_size=page_size,
            date_from=date_from,
            total=result.count,
        )

    return EventsListResponse(
        count=result.count,
        next=next_link,
        previous=previous_link,
        results=[
            EventListItemSchema(
                id=event.id,
                name=event.name,
                place=PlaceListSchema(
                    id=event.place.id,
                    name=event.place.name,
                    city=event.place.city,
                    address=event.place.address,
                ),
                event_time=event.event_time,
                registration_deadline=event.registration_deadline,
                status=event.status,
                number_of_visitors=event.number_of_visitors,
            )
            for event in result.results
        ],
    )


@router.get("/api/events/{event_id}/", response_model=EventDetailSchema)
async def get_event(
    event_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> EventDetailSchema:
    usecase: GetEventUsecase = get_get_event_usecase(session)
    try:
        event = await usecase.do(event_id)
    except EventNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        ) from exc

    return EventDetailSchema(
        id=event.id,
        name=event.name,
        place=PlaceDetailSchema(
            id=event.place.id,
            name=event.place.name,
            city=event.place.city,
            address=event.place.address,
            seats_pattern=event.place.seats_pattern or "",
        ),
        event_time=event.event_time,
        registration_deadline=event.registration_deadline,
        status=event.status,
        number_of_visitors=event.number_of_visitors,
    )


@router.get("/api/events/{event_id}/seats/", response_model=SeatsResponse)
async def get_event_seats(
    event_id: UUID,
    session: AsyncSession = Depends(get_session),
    client: EventsProviderClient = Depends(get_provider_client),
    cache: SeatsCache = Depends(get_seats_cache),
) -> SeatsResponse:
    usecase: GetSeatsUsecase = get_get_seats_usecase(session, client, cache)
    try:
        seats = await usecase.do(event_id)
    except EventNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        ) from exc
    except ProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return SeatsResponse(event_id=event_id, available_seats=seats)
