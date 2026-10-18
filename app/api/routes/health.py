from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/api/health/", include_in_schema=True)
@router.get("/api/health", include_in_schema=False)
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
