from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ReservationCreateRequest(BaseModel):
    """
    予約登録APIのリクエストスキーマ。

    新規予約作成時に必要な入力項目と、
    開始日時・終了日時の基本的なバリデーションルールを定義する。
    """

    user_id: int = Field(
        ...,
        ge=1,
        description="予約者のユーザーID",
    )
    meeting_room_id: int = Field(
        ...,
        ge=1,
        description="予約対象の会議室ID",
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="予約タイトル",
    )
    start_at: datetime = Field(
        ...,
        description="予約開始日時",
    )
    end_at: datetime = Field(
        ...,
        description="予約終了日時",
    )

    @model_validator(mode="after")
    def validate_time_range(self) -> "ReservationCreateRequest":
        """
        予約開始日時が終了日時より前であることを検証する。

        Returns:
            バリデーション済みの予約登録リクエスト。

        Raises:
            ValueError: 開始日時が終了日時以降の場合。
        """
        if self.start_at >= self.end_at:
            raise ValueError("start_at must be before end_at")

        return self


class ReservationUpdateRequest(BaseModel):
    """
    予約更新APIのリクエストスキーマ。

    既存予約の予約者、会議室、タイトル、予約時間、有効状態を
    更新するための入力項目とバリデーションルールを定義する。
    """

    user_id: int = Field(
        ...,
        ge=1,
        description="予約者のユーザーID",
    )
    meeting_room_id: int = Field(
        ...,
        ge=1,
        description="予約対象の会議室ID",
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="予約タイトル",
    )
    start_at: datetime = Field(
        ...,
        description="予約開始日時",
    )
    end_at: datetime = Field(
        ...,
        description="予約終了日時",
    )
    is_active: bool = Field(
        ...,
        description="有効な予約かどうか",
    )

    @model_validator(mode="after")
    def validate_time_range(self) -> "ReservationUpdateRequest":
        """
        予約開始日時が終了日時より前であることを検証する。

        Returns:
            バリデーション済みの予約更新リクエスト。

        Raises:
            ValueError: 開始日時が終了日時以降の場合。
        """
        if self.start_at >= self.end_at:
            raise ValueError("start_at must be before end_at")

        return self


class ReservationResponse(BaseModel):
    """
    予約情報を返却するためのレスポンススキーマ。

    DBモデルのReservationから、APIレスポンスとして必要な項目を返す。
    """

    id: int
    user_id: int
    meeting_room_id: int
    title: str
    start_at: datetime
    end_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)