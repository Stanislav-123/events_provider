from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_provider_client, get_session, get_sync_events_usecase
from app.api.schemas.sync import SyncTriggerResponse
from app.clients.events_provider import EventsProviderClient
from app.domain.exceptions import ProviderError, SyncAlreadyRunning
from app.usecases.sync_events import SyncEventsUsecase

router = APIRouter(tags=["sync"])


@router.post("/api/sync/trigger/", response_model=SyncTriggerResponse)
async def trigger_sync(
    session: AsyncSession = Depends(get_session),
    client: EventsProviderClient = Depends(get_provider_client),
) -> SyncTriggerResponse:
    usecase: SyncEventsUsecase = get_sync_events_usecase(session, client)
    try:
        result = await usecase.do()
    except SyncAlreadyRunning as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Synchronization is already running",
        ) from exc
    except ProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return SyncTriggerResponse(
        status=result["status"],
        processed=result["processed"],
        last_changed_at=result["last_changed_at"],
    )
