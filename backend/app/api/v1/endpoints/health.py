from fastapi import APIRouter

from app.schemas.health import HealthResponse
from app.services.health_service import HealthService

router = APIRouter()


@router.get("", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthService.check()