from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    APIリクエストごとにDBセッションを生成する。

    FastAPIの依存性注入で使用し、処理完了後に必ずセッションを閉じる。
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()