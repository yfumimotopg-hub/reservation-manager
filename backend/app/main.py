from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.db.session import AsyncSessionLocal, async_engine
from app.models.base import Base
from app.models.meeting_room import MeetingRoom
from app.models.reservation import Reservation
from app.models.user import User
from app.services.meeting_room_service import MeetingRoomService
from app.services.user_service import UserService


async def create_tables() -> None:
    """
    SQLAlchemyモデルをもとにDBテーブルを非同期で作成する。

    開発初期段階のため、アプリケーション起動時に未作成のテーブルを作成する。
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def create_seed_data() -> None:
    """
    開発環境用の初期データを非同期で作成する。

    ユーザー一覧APIや会議室一覧APIの動作確認をしやすくするため、
    サンプルデータを登録する。
    """
    async with AsyncSessionLocal() as db:
        await UserService.create_initial_users(db)
        await MeetingRoomService.create_initial_meeting_rooms(db)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    FastAPIアプリケーションの起動時・終了時処理を管理する。

    起動時にDBテーブル作成と初期データ投入を行い、
    アプリケーション終了時にDBエンジンを破棄する。
    """
    await create_tables()
    await create_seed_data()

    yield

    await async_engine.dispose()


def create_app() -> FastAPI:
    """
    FastAPIアプリケーションを生成する。

    lifespanを設定し、ルーティングなどアプリケーション起動時に必要な初期設定を行う。
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.API_VERSION,
        lifespan=lifespan,
    )

    app.include_router(api_router)

    return app


app = create_app()