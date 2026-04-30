from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    login_request: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    ログイン認証を行うAPIエンドポイント。

    メールアドレスとパスワードを検証し、
    認証に成功した場合はJWTアクセストークンを返却する。
    """
    return await AuthService.login(
        db=db,
        login_request=login_request,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """
    ログイン中ユーザー情報を取得するAPIエンドポイント。

    AuthorizationヘッダーのBearerトークンからユーザーを特定し、
    現在ログイン中のユーザー情報を返却する。
    """
    return current_user