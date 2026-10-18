from collections.abc import AsyncIterator
from typing import Any, Protocol


class SupportsEventPages(Protocol):
    async def get_events(
        self,
        changed_at: str,
        cursor_url: str | None = None,
    ) -> dict[str, Any]: ...


class EventsPaginator(AsyncIterator[dict[str, Any]]):
    """Async iterator that walks through all provider event pages."""

    def __init__(
        self,
        client: SupportsEventPages,
        changed_at: str = "2000-01-01",
    ) -> None:
        self._client = client
        self._changed_at = changed_at
        self._cursor_url: str | None = None
        self._buffer: list[dict[str, Any]] = []
        self._index = 0
        self._exhausted = False

    def __aiter__(self) -> "EventsPaginator":
        return self

    async def __anext__(self) -> dict[str, Any]:
        while self._index >= len(self._buffer):
            if self._exhausted:
                raise StopAsyncIteration
            await self._fetch_next_page()

        event = self._buffer[self._index]
        self._index += 1
        return event

    async def _fetch_next_page(self) -> None:
        page = await self._client.get_events(
            changed_at=self._changed_at,
            cursor_url=self._cursor_url,
        )
        self._buffer = list(page.get("results") or [])
        self._index = 0
        next_url = page.get("next")
        if next_url:
            self._cursor_url = next_url
        else:
            self._exhausted = True
            self._cursor_url = None
