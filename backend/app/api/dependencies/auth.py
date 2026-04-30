from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository


bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    AuthorizationヘッダーのBearerトークンからログイン中ユーザーを取得する。

    Args:
        credentials: HTTP Bearer認証情報。
        db: SQLAlchemyの非同期DBセッション。

    Returns:
        ログイン中ユーザー。

    Raises:
        HTTPException: トークンが不正、ユーザーが存在しない、または無効な場合。
    """
    user_id = decode_access_token(credentials.credentials)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    user = await UserRepository.find_by_id(
        db=db,
        user_id=int(user_id),
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    ログイン中ユーザーが管理者権限を持っていることを確認する。

    Args:
        current_user: ログイン中ユーザー。

    Returns:
        管理者権限を持つログイン中ユーザー。

    Raises:
        HTTPException: 管理者権限を持たない場合。
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permission required",
        )

    return current_user