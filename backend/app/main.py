from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings


def create_app() -> FastAPI:
    """
    FastAPIアプリケーションを生成する。

    ルーティング設定など、アプリケーション起動時に必要な初期設定を行う。
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.API_VERSION,
    )

    app.include_router(api_router)

    return app


app = create_app()