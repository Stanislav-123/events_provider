from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PlaceListSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    city: str
    address: str


class PlaceDetailSchema(PlaceListSchema):
    seats_pattern: str


class EventListItemSchema(BaseModel):
    id: UUID
    name: str
    place: PlaceListSchema
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int


class EventDetailSchema(BaseModel):
    id: UUID
    name: str
    place: PlaceDetailSchema
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int


class EventsListResponse(BaseModel):
    count: int
    next: str | None
    previous: str | None
    results: list[EventListItemSchema]


class SeatsResponse(BaseModel):
    event_id: UUID
    available_seats: list[str]


class EventsQuery(BaseModel):
    date_from: date | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
