from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserCreateRequest, UserResponse
from app.services.user_service import UserService

router = APIRouter()


@router.get("", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)) -> list[UserResponse]:
    """
    ユーザー一覧を取得するAPIエンドポイント。

    DBに登録されているユーザー情報を一覧で返却する。
    """
    return UserService.get_users(db)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user_create: UserCreateRequest,
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    新規ユーザーを登録するAPIエンドポイント。

    リクエスト内容をもとにユーザーを作成し、
    登録されたユーザー情報を返却する。
    """
    return UserService.create_user(
        db=db,
        user_create=user_create,
    )