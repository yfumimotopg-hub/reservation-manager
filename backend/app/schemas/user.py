from pydantic import BaseModel, ConfigDict


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