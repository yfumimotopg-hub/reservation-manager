from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserCreateRequest, UserResponse, UserUpdateRequest
from app.services.user_service import UserService

router = APIRouter()


@router.get("", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)) -> list[UserResponse]:
    """
    ユーザー一覧を取得するAPIエンドポイント。

    DBに登録されているユーザー情報を一覧で返却する。
    """
    return UserService.get_users(db)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    ユーザー詳細を取得するAPIエンドポイント。

    パスパラメータで指定されたユーザーIDに該当するユーザー情報を返却する。
    """
    return UserService.get_user(
        db=db,
        user_id=user_id,
    )


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


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdateRequest,
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    ユーザー情報を更新するAPIエンドポイント。

    パスパラメータで指定されたユーザーIDのユーザー情報を、
    リクエスト内容で更新する。
    """
    return UserService.update_user(
        db=db,
        user_id=user_id,
        user_update=user_update,
    )


@router.delete("/{user_id}", response_model=UserResponse)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    ユーザーを無効化するAPIエンドポイント。

    DBから物理削除せず、is_activeをFalseに更新する。
    """
    return UserService.deactivate_user(
        db=db,
        user_id=user_id,
    )