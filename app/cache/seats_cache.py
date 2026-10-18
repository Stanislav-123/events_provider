import time
from threading import Lock
from uuid import UUID


class SeatsCache:
    """Simple in-memory TTL cache for available seats."""

    def __init__(self, ttl_seconds: int = 30) -> None:
        self._ttl_seconds = ttl_seconds
        self._items: dict[str, tuple[float, list[str]]] = {}
        self._lock = Lock()

    def get(self, event_id: str | UUID) -> list[str] | None:
        key = str(event_id)
        with self._lock:
            item = self._items.get(key)
            if item is None:
                return None
            expires_at, seats = item
            if time.monotonic() >= expires_at:
                del self._items[key]
                return None
            return list(seats)

    def set(self, event_id: str | UUID, seats: list[str]) -> None:
        key = str(event_id)
        with self._lock:
            self._items[key] = (
                time.monotonic() + self._ttl_seconds,
                list(seats),
            )

    def clear(self) -> None:
        with self._lock:
            self._items.clear()
