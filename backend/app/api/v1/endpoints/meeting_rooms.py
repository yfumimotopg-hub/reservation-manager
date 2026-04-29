from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.meeting_room import (
    MeetingRoomCreateRequest,
    MeetingRoomResponse,
    MeetingRoomUpdateRequest,
)
from app.services.meeting_room_service import MeetingRoomService

router = APIRouter()


@router.get("", response_model=list[MeetingRoomResponse])
def get_meeting_rooms(
    db: Session = Depends(get_db),
) -> list[MeetingRoomResponse]:
    """
    会議室一覧を取得するAPIエンドポイント。

    DBに登録されている会議室情報を一覧で返却する。
    """
    return MeetingRoomService.get_meeting_rooms(db)


@router.get("/{meeting_room_id}", response_model=MeetingRoomResponse)
def get_meeting_room(
    meeting_room_id: int,
    db: Session = Depends(get_db),
) -> MeetingRoomResponse:
    """
    会議室詳細を取得するAPIエンドポイント。

    パスパラメータで指定された会議室IDに該当する会議室情報を返却する。
    """
    return MeetingRoomService.get_meeting_room(
        db=db,
        meeting_room_id=meeting_room_id,
    )


@router.post(
    "",
    response_model=MeetingRoomResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_meeting_room(
    meeting_room_create: MeetingRoomCreateRequest,
    db: Session = Depends(get_db),
) -> MeetingRoomResponse:
    """
    新規会議室を登録するAPIエンドポイント。

    リクエスト内容をもとに会議室を作成し、
    登録された会議室情報を返却する。
    """
    return MeetingRoomService.create_meeting_room(
        db=db,
        meeting_room_create=meeting_room_create,
    )


@router.put("/{meeting_room_id}", response_model=MeetingRoomResponse)
def update_meeting_room(
    meeting_room_id: int,
    meeting_room_update: MeetingRoomUpdateRequest,
    db: Session = Depends(get_db),
) -> MeetingRoomResponse:
    """
    会議室情報を更新するAPIエンドポイント。

    パスパラメータで指定された会議室IDの会議室情報を、
    リクエスト内容で更新する。
    """
    return MeetingRoomService.update_meeting_room(
        db=db,
        meeting_room_id=meeting_room_id,
        meeting_room_update=meeting_room_update,
    )


@router.delete("/{meeting_room_id}", response_model=MeetingRoomResponse)
def deactivate_meeting_room(
    meeting_room_id: int,
    db: Session = Depends(get_db),
) -> MeetingRoomResponse:
    """
    会議室を無効化するAPIエンドポイント。

    DBから物理削除せず、is_activeをFalseに更新する。
    """
    return MeetingRoomService.deactivate_meeting_room(
        db=db,
        meeting_room_id=meeting_room_id,
    )