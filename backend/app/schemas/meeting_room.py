from pydantic import BaseModel, ConfigDict, Field


class MeetingRoomCreateRequest(BaseModel):
    """
    会議室登録APIのリクエストスキーマ。

    新規会議室作成時に必要な入力項目と、
    入力値のバリデーションルールを定義する。
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="会議室名",
    )
    capacity: int = Field(
        ...,
        ge=1,
        description="定員",
    )
    location: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="設置場所",
    )


class MeetingRoomUpdateRequest(BaseModel):
    """
    会議室更新APIのリクエストスキーマ。

    既存会議室の名称、定員、設置場所、有効状態を更新するための
    入力項目とバリデーションルールを定義する。
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="会議室名",
    )
    capacity: int = Field(
        ...,
        ge=1,
        description="定員",
    )
    location: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="設置場所",
    )
    is_active: bool = Field(
        ...,
        description="有効な会議室かどうか",
    )


class MeetingRoomResponse(BaseModel):
    """
    会議室情報を返却するためのレスポンススキーマ。

    DBモデルのMeetingRoomから、APIレスポンスとして必要な項目を返す。
    """

    id: int
    name: str
    capacity: int
    location: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)