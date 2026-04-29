from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.meeting_room import MeetingRoom
from app.repositories.meeting_room_repository import MeetingRoomRepository
from app.schemas.meeting_room import (
    MeetingRoomCreateRequest,
    MeetingRoomUpdateRequest,
)


class MeetingRoomService:
    """
    会議室情報に関する業務処理を担当するサービス。

    API層から呼び出され、会議室の存在確認や重複チェックなどの
    業務ルールを扱う。
    """

    @staticmethod
    def get_meeting_rooms(db: Session) -> list[MeetingRoom]:
        """
        会議室一覧を取得する。

        Args:
            db: SQLAlchemyのDBセッション。

        Returns:
            会議室情報の一覧。
        """
        return MeetingRoomRepository.find_all(db)

    @staticmethod
    def get_meeting_room(db: Session, meeting_room_id: int) -> MeetingRoom:
        """
        指定されたIDの会議室を取得する。

        会議室が存在しない場合は404エラーを返す。

        Args:
            db: SQLAlchemyのDBセッション。
            meeting_room_id: 取得対象の会議室ID。

        Returns:
            会議室情報。

        Raises:
            HTTPException: 会議室が存在しない場合。
        """
        meeting_room = MeetingRoomRepository.find_by_id(
            db=db,
            meeting_room_id=meeting_room_id,
        )

        if meeting_room is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting room not found",
            )

        return meeting_room

    @staticmethod
    def create_meeting_room(
        db: Session,
        meeting_room_create: MeetingRoomCreateRequest,
    ) -> MeetingRoom:
        """
        新規会議室を登録する。

        会議室名の重複を確認し、既に登録済みの場合は409エラーを返す。

        Args:
            db: SQLAlchemyのDBセッション。
            meeting_room_create: 会議室登録リクエスト。

        Returns:
            登録された会議室情報。

        Raises:
            HTTPException: 会議室名が既に使用されている場合。
        """
        existing_meeting_room = MeetingRoomRepository.find_by_name(
            db=db,
            name=meeting_room_create.name,
        )

        if existing_meeting_room:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Meeting room name already exists",
            )

        return MeetingRoomRepository.create(
            db=db,
            meeting_room_create=meeting_room_create,
        )

    @staticmethod
    def update_meeting_room(
        db: Session,
        meeting_room_id: int,
        meeting_room_update: MeetingRoomUpdateRequest,
    ) -> MeetingRoom:
        """
        指定されたIDの会議室情報を更新する。

        更新対象会議室の存在確認と、会議室名の重複確認を行ったうえで更新する。

        Args:
            db: SQLAlchemyのDBセッション。
            meeting_room_id: 更新対象の会議室ID。
            meeting_room_update: 会議室更新リクエスト。

        Returns:
            更新後の会議室情報。

        Raises:
            HTTPException: 会議室が存在しない場合、または会議室名が重複している場合。
        """
        meeting_room = MeetingRoomService.get_meeting_room(
            db=db,
            meeting_room_id=meeting_room_id,
        )

        existing_meeting_room = MeetingRoomRepository.find_by_name(
            db=db,
            name=meeting_room_update.name,
        )

        if existing_meeting_room and existing_meeting_room.id != meeting_room_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Meeting room name already exists",
            )

        return MeetingRoomRepository.update(
            db=db,
            meeting_room=meeting_room,
            meeting_room_update=meeting_room_update,
        )

    @staticmethod
    def deactivate_meeting_room(
        db: Session,
        meeting_room_id: int,
    ) -> MeetingRoom:
        """
        指定されたIDの会議室を無効化する。

        物理削除ではなくis_activeをFalseに更新する。
        既に無効化されている会議室の場合は409エラーを返す。

        Args:
            db: SQLAlchemyのDBセッション。
            meeting_room_id: 無効化対象の会議室ID。

        Returns:
            無効化後の会議室情報。

        Raises:
            HTTPException: 会議室が存在しない場合、または既に無効化済みの場合。
        """
        meeting_room = MeetingRoomService.get_meeting_room(
            db=db,
            meeting_room_id=meeting_room_id,
        )

        if not meeting_room.is_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Meeting room is already inactive",
            )

        return MeetingRoomRepository.deactivate(
            db=db,
            meeting_room=meeting_room,
        )

    @staticmethod
    def create_initial_meeting_rooms(db: Session) -> None:
        """
        開発環境用の初期会議室データを作成する。

        会議室一覧APIの動作確認をしやすくするため、
        初回起動時にサンプル会議室を登録する。
        """
        MeetingRoomRepository.create_initial_meeting_rooms(db)