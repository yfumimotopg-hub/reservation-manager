from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    アプリケーション全体で使用する設定値を管理するクラス。

    環境変数からDB接続情報、API設定、JWT認証設定を読み込み、
    アプリケーション内で共通して参照できるようにする。
    """

    APP_NAME: str = "Simple Reservation Manager API"
    API_VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"

    DB_HOST: str = "db"
    DB_PORT: int = 3306
    DB_NAME: str = "reservation"
    DB_USER: str = "app_user"
    DB_PASSWORD: str = "app_password"

    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    @property
    def database_url(self) -> str:
        """
        SQLAlchemyの非同期DB接続URLを生成する。

        MySQLへasyncmyドライバ経由で接続するためのURLを返す。
        """
        return (
            f"mysql+asyncmy://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()