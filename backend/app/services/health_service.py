from app.schemas.health import HealthResponse


class HealthService:
    @staticmethod
    def check() -> HealthResponse:
        return HealthResponse(
            status="ok",
            message="API is running",
        )