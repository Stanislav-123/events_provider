from fastapi import APIRouter

from app.api.routes import events, health, sync, tickets


def build_api_router() -> APIRouter:
    router = APIRouter()
    router.include_router(health.router)
    router.include_router(events.router)
    router.include_router(tickets.router)
    router.include_router(sync.router)
    return router
