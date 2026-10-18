from typing import Any
from uuid import UUID

import httpx

from app.domain.exceptions import ProviderError


class EventsProviderClient:
    """HTTP client for the external Events Provider API."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._headers = {"x-api-key": api_key}
        self._client = client
        self._owns_client = client is None

    async def __aenter__(self) -> "EventsProviderClient":
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                follow_redirects=True,
            )
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()
            self._client = None

    def _http(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("EventsProviderClient is not started")
        return self._client

    async def get_events(
        self,
        changed_at: str,
        cursor_url: str | None = None,
    ) -> dict[str, Any]:
        """Fetch one page of events from the provider."""
        url = cursor_url or f"{self._base_url}/api/events/"
        params = None if cursor_url else {"changed_at": changed_at}

        response = await self._http().get(
            url,
            headers=self._headers,
            params=params,
        )
        self._raise_for_status(response)
        return response.json()

    async def get_seats(self, event_id: str | UUID) -> list[str]:
        """Fetch currently available seats for an event."""
        response = await self._http().get(
            f"{self._base_url}/api/events/{event_id}/seats/",
            headers=self._headers,
        )
        self._raise_for_status(response)
        payload = response.json()

        if isinstance(payload, list):
            return [str(seat) for seat in payload]

        seats = payload.get("available_seats")
        if seats is None:
            raise ProviderError("Unexpected seats response from provider")
        return [str(seat) for seat in seats]

    async def register(
        self,
        event_id: str | UUID,
        first_name: str,
        last_name: str,
        email: str,
        seat: str,
    ) -> str:
        """Register a visitor and return the created ticket id."""
        response = await self._http().post(
            f"{self._base_url}/api/events/{event_id}/register/",
            headers=self._headers,
            json={
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "seat": seat,
            },
        )
        self._raise_for_status(response)
        payload = response.json()

        ticket_id = payload.get("ticket_id") or payload.get("id")
        if not ticket_id:
            raise ProviderError("Provider did not return ticket id")
        return str(ticket_id)

    async def unregister(
        self,
        event_id: str | UUID,
        ticket_id: str | UUID,
    ) -> None:
        """Cancel a registration in the provider."""
        response = await self._http().request(
            "DELETE",
            f"{self._base_url}/api/events/{event_id}/unregister/",
            headers=self._headers,
            json={"ticket_id": str(ticket_id)},
        )
        self._raise_for_status(response)

    def _raise_for_status(self, response: httpx.Response) -> None:
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text
            raise ProviderError(
                f"Provider request failed with {exc.response.status_code}: {detail}"
            ) from exc
