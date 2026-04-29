from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.meeting_room import MeetingRoom
from app.schemas.meeting_room import (
    MeetingRoomCreateRequest,
    MeetingRoomUpdateRequest,
)


class MeetingRoomRepository:
    """
    会議室情報に関するDB操作を担当するリポジトリ。

    SQLAlchemyのAsyncSessionを使用し、非同期で検索・登録・更新・無効化などの
    DBアクセス処理を行う。
    """

    @staticmethod
    async def find_all(db: AsyncSession) -> list[MeetingRoom]:
        """
        登録されている全会議室を非同期で取得する。

        Args:
            db: SQLAlchemyの非同期DBセッション。

        Returns:
            会議室情報の一覧。
        """
        result = await db.execute(
            select(MeetingRoom).order_by(MeetingRoom.id)
        )
        return list(result.scalars().all())

    @staticmethod
    async def find_by_id(
        db: AsyncSession,
        meeting_room_id: int,
    ) -> MeetingRoom | None:
        """
        会議室IDを条件に会議室を1件非同期で取得する。

        Args:
            db: SQLAlchemyの非同期DBセッション。
            meeting_room_id: 検索対象の会議室ID。

        Returns:
            該当する会議室。存在しない場合はNone。
        """
        result = await db.execute(
            select(MeetingRoom).where(MeetingRoom.id == meeting_room_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def find_by_name(
        db: AsyncSession,
        name: str,
    ) -> MeetingRoom | None:
        """
        会議室名を条件に会議室を1件非同期で取得する。

        Args:
            db: SQLAlchemyの非同期DBセッション。
            name: 検索対象の会議室名。

        Returns:
            該当する会議室。存在しない場合はNone。
        """
        result = await db.execute(
            select(MeetingRoom).where(MeetingRoom.name == name)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
        db: AsyncSession,
        meeting_room_create: MeetingRoomCreateRequest,
    ) -> MeetingRoom:
        """
        新規会議室を非同期で登録する。

        Args:
            db: SQLAlchemyの非同期DBセッション。
            meeting_room_create: 会議室登録リクエスト。

        Returns:
            登録された会議室情報。
        """
        meeting_room = MeetingRoom(
            name=meeting_room_create.name,
            capacity=meeting_room_create.capacity,
            location=meeting_room_create.location,
            is_active=True,
        )

        db.add(meeting_room)
        await db.commit()
        await db.refresh(meeting_room)

        return meeting_room

    @staticmethod
    async def update(
        db: AsyncSession,
        meeting_room: MeetingRoom,
        meeting_room_update: MeetingRoomUpdateRequest,
    ) -> MeetingRoom:
        """
        既存会議室情報を非同期で更新する。

        Args:
            db: SQLAlchemyの非同期DBセッション。
            meeting_room: 更新対象の会議室。
            meeting_room_update: 会議室更新リクエスト。

        Returns:
            更新後の会議室情報。
        """
        meeting_room.name = meeting_room_update.name
        meeting_room.capacity = meeting_room_update.capacity
        meeting_room.location = meeting_room_update.location
        meeting_room.is_active = meeting_room_update.is_active

        await db.commit()
        await db.refresh(meeting_room)

        return meeting_room

    @staticmethod
    async def deactivate(
        db: AsyncSession,
        meeting_room: MeetingRoom,
    ) -> MeetingRoom:
        """
        会議室を非同期で無効化する。

        物理削除は行わず、is_activeをFalseに更新することで、
        過去の予約データとの紐づきを維持する。

        Args:
            db: SQLAlchemyの非同期DBセッション。
            meeting_room: 無効化対象の会議室。

        Returns:
            無効化後の会議室情報。
        """
        meeting_room.is_active = False

        await db.commit()
        await db.refresh(meeting_room)

        return meeting_room

    @staticmethod
    async def create_initial_meeting_rooms(db: AsyncSession) -> None:
        """
        初期表示確認用の会議室データを非同期で作成する。

        会議室が1件も存在しない場合のみ、サンプル会議室を登録する。
        """
        result = await db.execute(select(MeetingRoom).limit(1))
        exists_meeting_room = result.scalar_one_or_none()

        if exists_meeting_room:
            return

        meeting_rooms = [
            MeetingRoom(
                name="会議室A",
                capacity=6,
                location="3F",
                is_active=True,
            ),
            MeetingRoom(
                name="会議室B",
                capacity=12,
                location="4F",
                is_active=True,
            ),
        ]

        db.add_all(meeting_rooms)
        await db.commit()