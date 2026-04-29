from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.database import DatabaseHealthResponse
from app.services.database_service import DatabaseService

router = APIRouter()


@router.get("/health", response_model=DatabaseHealthResponse)
def database_health_check(db: Session = Depends(get_db)) -> DatabaseHealthResponse:
    """
    DB接続状態を確認するAPIエンドポイント。

    MySQLへ接続できるか確認し、接続できる場合は正常レスポンスを返す。
    """
    return DatabaseService.check_connection(db)