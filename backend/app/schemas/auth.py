from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """
    ログインAPIのリクエストスキーマ。

    メールアドレスとパスワードを受け取り、認証に使用する。
    """

    email: EmailStr = Field(
        ...,
        description="メールアドレス",
    )
    password: str = Field(
        ...,
        min_length=1,
        description="パスワード",
    )


class TokenResponse(BaseModel):
    """
    ログイン成功時に返却するトークンレスポンススキーマ。
    """

    access_token: str
    token_type: str = "bearer"