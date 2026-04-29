from fastapi import APIRouter

from app.api.v1.endpoints import database, health, meeting_rooms, users

router = APIRouter()

router.include_router(
    health.router,
    prefix="/health",
    tags=["health"],
)

router.include_router(
    database.router,
    prefix="/database",
    tags=["database"],
)

router.include_router(
    users.router,
    prefix="/users",
    tags=["users"],
)

router.include_router(
    meeting_rooms.router,
    prefix="/meeting-rooms",
    tags=["meeting-rooms"],
)