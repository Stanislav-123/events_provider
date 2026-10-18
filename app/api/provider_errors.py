from fastapi import HTTPException, status

from app.domain.exceptions import ProviderError


def http_exception_from_provider(exc: ProviderError) -> HTTPException:
    """Map provider failures to client-facing HTTP errors."""
    if exc.status_code is not None and 400 <= exc.status_code < 500:
        return HTTPException(status_code=exc.status_code, detail=str(exc))
    return HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=str(exc),
    )
