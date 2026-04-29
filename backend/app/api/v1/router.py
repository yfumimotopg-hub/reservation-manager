from fastapi import APIRouter

from app.api.v1.endpoints import database, health

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