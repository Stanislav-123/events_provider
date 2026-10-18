from app.domain.entities import EventEntity, PlaceEntity, TicketEntity
from app.models.event import Event
from app.models.place import Place
from app.models.ticket import Ticket


def place_to_entity(place: Place, *, include_seats_pattern: bool) -> PlaceEntity:
    return PlaceEntity(
        id=place.id,
        name=place.name,
        city=place.city,
        address=place.address,
        seats_pattern=place.seats_pattern if include_seats_pattern else None,
    )


def event_to_entity(
    event: Event,
    *,
    include_seats_pattern: bool = False,
) -> EventEntity:
    return EventEntity(
        id=event.id,
        name=event.name,
        place=place_to_entity(
            event.place,
            include_seats_pattern=include_seats_pattern,
        ),
        event_time=event.event_time,
        registration_deadline=event.registration_deadline,
        status=event.status,
        number_of_visitors=event.number_of_visitors,
    )


def ticket_to_entity(ticket: Ticket) -> TicketEntity:
    return TicketEntity(
        ticket_id=ticket.id,
        event_id=ticket.event_id,
        first_name=ticket.first_name,
        last_name=ticket.last_name,
        email=ticket.email,
        seat=ticket.seat,
    )
