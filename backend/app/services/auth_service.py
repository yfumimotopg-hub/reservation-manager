from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse


class AuthService:
    """
    認証に関する業務処理を担当するサービス。

    ログイン認証、JWT発行、ログイン中ユーザーの取得を行う。
    """

    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        login_request: LoginRequest,
    ) -> User:
        """
        メールアドレスとパスワードを検証し、認証済みユーザーを取得する。

        Args:
            db: SQLAlchemyの非同期DBセッション。
            login_request: ログインリクエスト。

        Returns:
            認証済みユーザー。

        Raises:
            HTTPException: 認証情報が不正、またはユーザーが無効な場合。
        """
        user = await UserRepository.find_by_email(
            db=db,
            email=login_request.email,
        )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not verify_password(
            plain_password=login_request.password,
            password_hash=user.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user",
            )

        return user

    @staticmethod
    async def login(
        db: AsyncSession,
        login_request: LoginRequest,
    ) -> TokenResponse:
        """
        ログイン認証を行い、JWTアクセストークンを発行する。

        Args:
            db: SQLAlchemyの非同期DBセッション。
            login_request: ログインリクエスト。

        Returns:
            JWTアクセストークンレスポンス。
        """
        user = await AuthService.authenticate_user(
            db=db,
            login_request=login_request,
        )

        access_token = create_access_token(subject=str(user.id))

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
        )