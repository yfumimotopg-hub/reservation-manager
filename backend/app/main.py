from fastapi import FastAPI
from sqlalchemy.orm import Session

from app.api.router import api_router
from app.core.config import settings
from app.db.session import SessionLocal, engine
from app.models.base import Base
from app.models.meeting_room import MeetingRoom
from app.models.reservation import Reservation
from app.models.user import User
from app.services.meeting_room_service import MeetingRoomService
from app.services.user_service import UserService


def create_tables() -> None:
    """
    SQLAlchemyモデルをもとにDBテーブルを作成する。

    開発初期段階のため、アプリケーション起動時に未作成のテーブルを作成する。
    """
    Base.metadata.create_all(bind=engine)


def create_seed_data() -> None:
    """
    開発環境用の初期データを作成する。

    ユーザー一覧APIや会議室一覧APIの動作確認をしやすくするため、
    サンプルデータを登録する。
    """
    db: Session = SessionLocal()

    try:
        UserService.create_initial_users(db)
        MeetingRoomService.create_initial_meeting_rooms(db)
    finally:
        db.close()


def create_app() -> FastAPI:
    """
    FastAPIアプリケーションを生成する。

    ルーティング設定、DBテーブル作成、初期データ作成など、
    アプリケーション起動時に必要な初期設定を行う。
    """
    create_tables()
    create_seed_data()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.API_VERSION,
    )

    app.include_router(api_router)

    return app


app = create_app()