from unittest.mock import AsyncMock

import pytest

from app.clients.paginator import EventsPaginator


@pytest.mark.asyncio
async def test_paginator_yields_all_events_across_pages() -> None:
    client = AsyncMock()
    client.get_events.side_effect = [
        {
            "next": "https://provider/api/events/?cursor=2",
            "results": [{"id": "1"}, {"id": "2"}],
        },
        {
            "next": None,
            "results": [{"id": "3"}],
        },
    ]

    events = [event async for event in EventsPaginator(client, changed_at="2000-01-01")]

    assert [event["id"] for event in events] == ["1", "2", "3"]
    assert client.get_events.await_count == 2
    first_call = client.get_events.await_args_list[0]
    assert first_call.kwargs["changed_at"] == "2000-01-01"
    assert first_call.kwargs["cursor_url"] is None
    second_call = client.get_events.await_args_list[1]
    assert second_call.kwargs["cursor_url"] == "https://provider/api/events/?cursor=2"


@pytest.mark.asyncio
async def test_paginator_handles_empty_first_page() -> None:
    client = AsyncMock()
    client.get_events.return_value = {"next": None, "results": []}

    events = [event async for event in EventsPaginator(client)]

    assert events == []
    client.get_events.assert_awaited_once()
