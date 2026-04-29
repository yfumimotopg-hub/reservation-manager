from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


async_engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    APIリクエストごとに非同期DBセッションを生成する。

    FastAPIの依存性注入で使用し、処理完了後に必ずセッションを閉じる。
    """
    async with AsyncSessionLocal() as db:
        yield db