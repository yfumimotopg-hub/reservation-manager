from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """
    平文パスワードをハッシュ化する。

    DBには平文パスワードを保存せず、bcryptでハッシュ化した値のみを保存する。

    Args:
        password: 平文パスワード。

    Returns:
        ハッシュ化されたパスワード。
    """
    return password_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """
    平文パスワードとハッシュ化済みパスワードが一致するか検証する。

    Args:
        plain_password: ログイン時に入力された平文パスワード。
        password_hash: DBに保存されているハッシュ化済みパスワード。

    Returns:
        パスワードが一致する場合はTrue。
    """
    return password_context.verify(plain_password, password_hash)


def create_access_token(subject: str) -> str:
    """
    JWTアクセストークンを作成する。

    subjectにはユーザーを識別する値を設定する。
    今回はユーザーIDを文字列として格納する。

    Args:
        subject: トークンに格納するユーザー識別子。

    Returns:
        JWTアクセストークン。
    """
    expire = datetime.now(UTC) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": subject,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> str | None:
    """
    JWTアクセストークンを検証し、ユーザー識別子を取得する。

    Args:
        token: Authorizationヘッダーから取得したJWTアクセストークン。

    Returns:
        トークンが有効な場合はユーザー識別子。無効な場合はNone。
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        subject = payload.get("sub")

        if subject is None:
            return None

        return str(subject)
    except JWTError:
        return None