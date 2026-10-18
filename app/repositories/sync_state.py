from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import SyncMeta
from app.models.sync_state import SyncState

SINGLETON_ID = 1


class SyncStateRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self) -> SyncMeta:
        state = await self._ensure()
        return SyncMeta(
            last_sync_time=state.last_sync_time,
            last_changed_at=state.last_changed_at,
            sync_status=state.sync_status,
        )

    async def mark_running(self) -> None:
        state = await self._ensure()
        state.sync_status = "running"
        await self._session.commit()

    async def mark_success(
        self,
        *,
        sync_time: datetime,
        last_changed_at: datetime | None,
    ) -> None:
        state = await self._ensure()
        state.sync_status = "success"
        state.last_sync_time = sync_time
        if last_changed_at is not None:
            state.last_changed_at = last_changed_at
        await self._session.commit()

    async def mark_failed(self) -> None:
        await self._session.rollback()
        state = await self._ensure()
        state.sync_status = "failed"
        await self._session.commit()

    async def _ensure(self) -> SyncState:
        state = await self._session.get(SyncState, SINGLETON_ID)
        if state is None:
            state = SyncState(id=SINGLETON_ID, sync_status="idle")
            self._session.add(state)
            await self._session.flush()
        return state
