class AppError(Exception):
    """Base application error."""


class EventNotFound(AppError):
    """Requested event does not exist in the local database."""


class EventUnexpectedStatus(AppError):
    """Event is not available for the requested operation."""


class TicketNotFound(AppError):
    """Requested ticket does not exist in the local database."""


class ProviderError(AppError):
    """Events Provider API returned an error."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class SyncAlreadyRunning(AppError):
    """Another synchronization process is already running."""
