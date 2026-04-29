from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreateRequest(BaseModel):
    """
    ユーザー登録APIのリクエストスキーマ。

    新規ユーザー作成時に必要な入力項目と、
    入力値の基本的なバリデーションルールを定義する。
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="ユーザー名",
    )
    email: EmailStr = Field(
        ...,
        description="メールアドレス",
    )
    role: str = Field(
        default="user",
        min_length=1,
        max_length=50,
        description="ユーザー権限",
    )


class UserResponse(BaseModel):
    """
    ユーザー情報を返却するためのレスポンススキーマ。

    DBモデルのUserから、APIレスポンスとして必要な項目のみを返す。
    """

    id: int
    name: str
    email: str
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)