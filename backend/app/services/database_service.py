from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.database import DatabaseHealthResponse


class DatabaseService:
    """
    データベース接続に関する処理を提供するサービスクラス。
    """

    @staticmethod
    def check_connection(db: Session) -> DatabaseHealthResponse:
        """
        DBへ簡単なSQLを実行し、接続できるか確認する。

        Args:
            db: SQLAlchemyのDBセッション。

        Returns:
            DB接続確認結果。
        """
        db.execute(text("SELECT 1"))

        return DatabaseHealthResponse(
            status="ok",
            message="Database connection is healthy",
        )