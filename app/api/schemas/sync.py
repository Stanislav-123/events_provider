from pydantic import BaseModel


class SyncTriggerResponse(BaseModel):
    status: str
    processed: int
    last_changed_at: str | None = None
