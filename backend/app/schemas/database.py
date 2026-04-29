from pydantic import BaseModel


class DatabaseHealthResponse(BaseModel):
    """
    DB接続確認APIのレスポンス形式を定義するスキーマ。
    """

    status: str
    message: str