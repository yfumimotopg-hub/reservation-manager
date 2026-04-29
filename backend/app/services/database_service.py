from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.database import DatabaseHealthResponse


class DatabaseService:
    """
    データベース接続に関する処理を提供するサービスクラス。
    """

    @staticmethod
    async def check_connection(db: AsyncSession) -> DatabaseHealthResponse:
        """
        DBへ簡単なSQLを非同期で実行し、接続できるか確認する。

        Args:
            db: SQLAlchemyの非同期DBセッション。

        Returns:
            DB接続確認結果。
        """
        await db.execute(text("SELECT 1"))

        return DatabaseHealthResponse(
            status="ok",
            message="Database connection is healthy",
        )