from uuid import uuid4

import httpx
import pytest
import respx

from app.clients.events_provider import EventsProviderClient
from app.domain.exceptions import ProviderError

BASE_URL = "https://events-provider.test"


@pytest.fixture
async def client() -> EventsProviderClient:
    http = httpx.AsyncClient(follow_redirects=True)
    provider = EventsProviderClient(
        base_url=BASE_URL,
        api_key="test-api-key",
        client=http,
    )
    yield provider
    await http.aclose()


@respx.mock
@pytest.mark.asyncio
async def test_get_events_first_page(client: EventsProviderClient) -> None:
    route = respx.get(f"{BASE_URL}/api/events/").mock(
        return_value=httpx.Response(
            200,
            json={"next": None, "previous": None, "results": [{"id": "1"}]},
        )
    )

    payload = await client.get_events(changed_at="2000-01-01")

    assert payload["results"] == [{"id": "1"}]
    assert route.called
    assert route.calls.last.request.url.params["changed_at"] == "2000-01-01"
    assert route.calls.last.request.headers["x-api-key"] == "test-api-key"


@respx.mock
@pytest.mark.asyncio
async def test_get_events_follows_cursor_url(client: EventsProviderClient) -> None:
    cursor = f"{BASE_URL}/api/events/?cursor=abc"
    route = respx.get(cursor).mock(
        return_value=httpx.Response(
            200,
            json={"next": None, "results": [{"id": "2"}]},
        )
    )

    payload = await client.get_events(changed_at="2000-01-01", cursor_url=cursor)

    assert payload["results"][0]["id"] == "2"
    assert route.called
    assert "changed_at" not in route.calls.last.request.url.params


@respx.mock
@pytest.mark.asyncio
async def test_get_events_rewrites_public_cursor_host(
    client: EventsProviderClient,
) -> None:
    public_cursor = "http://events-provider.dev-2.python-labs.ru/api/events/?cursor=abc"
    route = respx.get(f"{BASE_URL}/api/events/?cursor=abc").mock(
        return_value=httpx.Response(
            200,
            json={"next": None, "results": [{"id": "3"}]},
        )
    )

    payload = await client.get_events(
        changed_at="2000-01-01",
        cursor_url=public_cursor,
    )

    assert payload["results"][0]["id"] == "3"
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_unregister_sends_ticket_id_json_body(
    client: EventsProviderClient,
) -> None:
    event_id = uuid4()
    ticket_id = uuid4()
    route = respx.delete(
        f"{BASE_URL}/api/events/{event_id}/unregister/"
    ).mock(return_value=httpx.Response(200, json={"success": True}))

    await client.unregister(event_id, ticket_id)

    assert route.called
    assert "ticket_id" not in route.calls.last.request.url.params
    assert route.calls.last.request.content == (
        f'{{"ticket_id":"{ticket_id}"}}'.encode()
    )


@respx.mock
@pytest.mark.asyncio
async def test_get_seats(client: EventsProviderClient) -> None:
    event_id = uuid4()
    respx.get(f"{BASE_URL}/api/events/{event_id}/seats/").mock(
        return_value=httpx.Response(
            200,
            json={"available_seats": ["A1", "A3"]},
        )
    )

    seats = await client.get_seats(event_id)

    assert seats == ["A1", "A3"]


@respx.mock
@pytest.mark.asyncio
async def test_register_returns_ticket_id(client: EventsProviderClient) -> None:
    event_id = uuid4()
    ticket_id = str(uuid4())
    route = respx.post(f"{BASE_URL}/api/events/{event_id}/register/").mock(
        return_value=httpx.Response(201, json={"ticket_id": ticket_id})
    )

    result = await client.register(
        event_id,
        first_name="Ivan",
        last_name="Ivanov",
        email="ivan@example.com",
        seat="A15",
    )

    assert result == ticket_id
    assert b"Ivan" in route.calls.last.request.content


@respx.mock
@pytest.mark.asyncio
async def test_provider_error_on_http_failure(client: EventsProviderClient) -> None:
    respx.get(f"{BASE_URL}/api/events/").mock(
        return_value=httpx.Response(500, text="boom")
    )

    with pytest.raises(ProviderError):
        await client.get_events(changed_at="2000-01-01")
