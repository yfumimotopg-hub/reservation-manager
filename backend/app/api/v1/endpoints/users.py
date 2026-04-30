from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreateRequest, UserResponse, UserUpdateRequest
from app.services.user_service import UserService

router = APIRouter()


@router.get("", response_model=list[UserResponse])
async def get_users(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[UserResponse]:
    """
    ユーザー一覧を取得するAPIエンドポイント。

    管理者権限を持つユーザーのみ、DBに登録されているユーザー情報を
    非同期で一覧取得して返却する。
    """
    return await UserService.get_users(db)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> UserResponse:
    """
    ユーザー詳細を取得するAPIエンドポイント。

    管理者権限を持つユーザーのみ、指定されたユーザーIDに該当する
    ユーザー情報を非同期で返却する。
    """
    return await UserService.get_user(
        db=db,
        user_id=user_id,
    )


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_create: UserCreateRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> UserResponse:
    """
    新規ユーザーを登録するAPIエンドポイント。

    管理者権限を持つユーザーのみ、リクエスト内容をもとにユーザーを
    非同期で作成し、登録されたユーザー情報を返却する。
    """
    return await UserService.create_user(
        db=db,
        user_create=user_create,
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> UserResponse:
    """
    ユーザー情報を更新するAPIエンドポイント。

    管理者権限を持つユーザーのみ、指定されたユーザーIDのユーザー情報を
    リクエスト内容で非同期更新する。
    """
    return await UserService.update_user(
        db=db,
        user_id=user_id,
        user_update=user_update,
    )


@router.delete("/{user_id}", response_model=UserResponse)
async def deactivate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> UserResponse:
    """
    ユーザーを無効化するAPIエンドポイント。

    管理者権限を持つユーザーのみ、DBから物理削除せず、
    is_activeをFalseに非同期で更新する。
    """
    return await UserService.deactivate_user(
        db=db,
        user_id=user_id,
    )