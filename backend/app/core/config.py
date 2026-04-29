from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Simple Reservation Manager API"
    API_VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"


settings = Settings()