from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user, require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.meeting_room import (
    MeetingRoomCreateRequest,
    MeetingRoomResponse,
    MeetingRoomUpdateRequest,
)
from app.services.meeting_room_service import MeetingRoomService

router = APIRouter()


@router.get("", response_model=list[MeetingRoomResponse])
async def get_meeting_rooms(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[MeetingRoomResponse]:
    """
    会議室一覧を取得するAPIエンドポイント。

    ログイン済みユーザーのみ、DBに登録されている会議室情報を
    非同期で一覧取得して返却する。
    """
    return await MeetingRoomService.get_meeting_rooms(db)


@router.get("/{meeting_room_id}", response_model=MeetingRoomResponse)
async def get_meeting_room(
    meeting_room_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> MeetingRoomResponse:
    """
    会議室詳細を取得するAPIエンドポイント。

    ログイン済みユーザーのみ、指定された会議室IDに該当する
    会議室情報を非同期で返却する。
    """
    return await MeetingRoomService.get_meeting_room(
        db=db,
        meeting_room_id=meeting_room_id,
    )


@router.post(
    "",
    response_model=MeetingRoomResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_meeting_room(
    meeting_room_create: MeetingRoomCreateRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> MeetingRoomResponse:
    """
    新規会議室を登録するAPIエンドポイント。

    管理者権限を持つユーザーのみ、リクエスト内容をもとに会議室を
    非同期で作成し、登録された会議室情報を返却する。
    """
    return await MeetingRoomService.create_meeting_room(
        db=db,
        meeting_room_create=meeting_room_create,
    )


@router.put("/{meeting_room_id}", response_model=MeetingRoomResponse)
async def update_meeting_room(
    meeting_room_id: int,
    meeting_room_update: MeetingRoomUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> MeetingRoomResponse:
    """
    会議室情報を更新するAPIエンドポイント。

    管理者権限を持つユーザーのみ、指定された会議室IDの会議室情報を
    リクエスト内容で非同期更新する。
    """
    return await MeetingRoomService.update_meeting_room(
        db=db,
        meeting_room_id=meeting_room_id,
        meeting_room_update=meeting_room_update,
    )


@router.delete("/{meeting_room_id}", response_model=MeetingRoomResponse)
async def deactivate_meeting_room(
    meeting_room_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> MeetingRoomResponse:
    """
    会議室を無効化するAPIエンドポイント。

    管理者権限を持つユーザーのみ、DBから物理削除せず、
    is_activeをFalseに非同期で更新する。
    """
    return await MeetingRoomService.deactivate_meeting_room(
        db=db,
        meeting_room_id=meeting_room_id,
    )