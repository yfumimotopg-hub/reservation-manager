from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reservation import Reservation
from app.schemas.reservation import (
    ReservationCreateRequest,
    ReservationUpdateRequest,
)


class ReservationRepository:
    """
    予約情報に関するDB操作を担当するリポジトリ。

    SQLAlchemyのAsyncSessionを使用し、非同期で検索・登録・更新・無効化などの
    DBアクセス処理を行う。
    """

    @staticmethod
    async def find_all(db: AsyncSession) -> list[Reservation]:
        """
        登録されている全予約を非同期で取得する。

        Args:
            db: SQLAlchemyの非同期DBセッション。

        Returns:
            予約情報の一覧。
        """
        result = await db.execute(
            select(Reservation).order_by(Reservation.start_at)
        )
        return list(result.scalars().all())

    @staticmethod
    async def find_by_user_id(
        db: AsyncSession,
        user_id: int,
    ) -> list[Reservation]:
        """
        指定されたユーザーIDに紐づく予約一覧を非同期で取得する。

        Args:
            db: SQLAlchemyの非同期DBセッション。
            user_id: 予約者ユーザーID。

        Returns:
            指定ユーザーの予約一覧。
        """
        result = await db.execute(
            select(Reservation)
            .where(Reservation.user_id == user_id)
            .order_by(Reservation.start_at)
        )
        return list(result.scalars().all())

    @staticmethod
    async def find_by_id(
        db: AsyncSession,
        reservation_id: int,
    ) -> Reservation | None:
        """
        予約IDを条件に予約を1件非同期で取得する。

        Args:
            db: SQLAlchemyの非同期DBセッション。
            reservation_id: 検索対象の予約ID。

        Returns:
            該当する予約。存在しない場合はNone。
        """
        result = await db.execute(
            select(Reservation).where(Reservation.id == reservation_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def exists_overlapping_reservation(
        db: AsyncSession,
        meeting_room_id: int,
        start_at: datetime,
        end_at: datetime,
        exclude_reservation_id: int | None = None,
    ) -> bool:
        """
        指定した会議室・時間帯に重複する有効な予約が存在するか非同期で確認する。

        Args:
            db: SQLAlchemyの非同期DBセッション。
            meeting_room_id: 確認対象の会議室ID。
            start_at: 予約開始日時。
            end_at: 予約終了日時。
            exclude_reservation_id: 更新時に重複判定から除外する予約ID。

        Returns:
            重複する予約が存在する場合はTrue。
        """
        statement = select(Reservation).where(
            Reservation.meeting_room_id == meeting_room_id,
            Reservation.is_active.is_(True),
            Reservation.start_at < end_at,
            Reservation.end_at > start_at,
        )

        if exclude_reservation_id is not None:
            statement = statement.where(
                Reservation.id != exclude_reservation_id
            )

        result = await db.execute(statement)

        return result.scalar_one_or_none() is not None

    @staticmethod
    async def create(
        db: AsyncSession,
        reservation_create: ReservationCreateRequest,
    ) -> Reservation:
        """
        新規予約を非同期で登録する。

        Args:
            db: SQLAlchemyの非同期DBセッション。
            reservation_create: 予約登録リクエスト。

        Returns:
            登録された予約情報。
        """
        reservation = Reservation(
            user_id=reservation_create.user_id,
            meeting_room_id=reservation_create.meeting_room_id,
            title=reservation_create.title,
            start_at=reservation_create.start_at,
            end_at=reservation_create.end_at,
            is_active=True,
        )

        db.add(reservation)
        await db.commit()
        await db.refresh(reservation)

        return reservation

    @staticmethod
    async def update(
        db: AsyncSession,
        reservation: Reservation,
        reservation_update: ReservationUpdateRequest,
    ) -> Reservation:
        """
        既存予約情報を非同期で更新する。

        Args:
            db: SQLAlchemyの非同期DBセッション。
            reservation: 更新対象の予約。
            reservation_update: 予約更新リクエスト。

        Returns:
            更新後の予約情報。
        """
        reservation.user_id = reservation_update.user_id
        reservation.meeting_room_id = reservation_update.meeting_room_id
        reservation.title = reservation_update.title
        reservation.start_at = reservation_update.start_at
        reservation.end_at = reservation_update.end_at
        reservation.is_active = reservation_update.is_active

        await db.commit()
        await db.refresh(reservation)

        return reservation

    @staticmethod
    async def deactivate(
        db: AsyncSession,
        reservation: Reservation,
    ) -> Reservation:
        """
        予約を非同期で無効化する。

        物理削除は行わず、is_activeをFalseに更新することで、
        予約履歴をDB上に残す。

        Args:
            db: SQLAlchemyの非同期DBセッション。
            reservation: 無効化対象の予約。

        Returns:
            無効化後の予約情報。
        """
        reservation.is_active = False

        await db.commit()
        await db.refresh(reservation)

        return reservation