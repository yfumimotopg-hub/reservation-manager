from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserResponse
from app.services.user_service import UserService

router = APIRouter()


@router.get("", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)) -> list[UserResponse]:
    """
    ユーザー一覧を取得するAPIエンドポイント。

    DBに登録されているユーザー情報を一覧で返却する。
    """
    return UserService.get_users(db)