from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reservation import Reservation
from app.repositories.meeting_room_repository import MeetingRoomRepository
from app.repositories.reservation_repository import ReservationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.reservation import (
    ReservationCreateRequest,
    ReservationUpdateRequest,
)


class ReservationService:
    """
    予約情報に関する業務処理を担当するサービス。

    ユーザー・会議室の存在確認、無効状態の確認、
    予約時間の重複チェックなどの業務ルールを非同期で扱う。
    """

    @staticmethod
    async def get_reservations(db: AsyncSession) -> list[Reservation]:
        """
        予約一覧を非同期で取得する。

        Args:
            db: SQLAlchemyの非同期DBセッション。

        Returns:
            予約情報の一覧。
        """
        return await ReservationRepository.find_all(db)

    @staticmethod
    async def get_reservation(
        db: AsyncSession,
        reservation_id: int,
    ) -> Reservation:
        """
        指定されたIDの予約を非同期で取得する。

        予約が存在しない場合は404エラーを返す。

        Args:
            db: SQLAlchemyの非同期DBセッション。
            reservation_id: 取得対象の予約ID。

        Returns:
            予約情報。

        Raises:
            HTTPException: 予約が存在しない場合。
        """
        reservation = await ReservationRepository.find_by_id(
            db=db,
            reservation_id=reservation_id,
        )

        if reservation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation not found",
            )

        return reservation

    @staticmethod
    async def validate_user(
        db: AsyncSession,
        user_id: int,
    ) -> None:
        """
        予約に利用するユーザーが存在し、有効状態であることを非同期で確認する。

        Args:
            db: SQLAlchemyの非同期DBセッション。
            user_id: 確認対象のユーザーID。

        Raises:
            HTTPException: ユーザーが存在しない、または無効状態の場合。
        """
        user = await UserRepository.find_by_id(
            db=db,
            user_id=user_id,
        )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User is inactive",
            )

    @staticmethod
    async def validate_meeting_room(
        db: AsyncSession,
        meeting_room_id: int,
    ) -> None:
        """
        予約に利用する会議室が存在し、有効状態であることを非同期で確認する。

        Args:
            db: SQLAlchemyの非同期DBセッション。
            meeting_room_id: 確認対象の会議室ID。

        Raises:
            HTTPException: 会議室が存在しない、または無効状態の場合。
        """
        meeting_room = await MeetingRoomRepository.find_by_id(
            db=db,
            meeting_room_id=meeting_room_id,
        )

        if meeting_room is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting room not found",
            )

        if not meeting_room.is_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Meeting room is inactive",
            )

    @staticmethod
    async def validate_no_overlap(
        db: AsyncSession,
        meeting_room_id: int,
        start_at: datetime,
        end_at: datetime,
        exclude_reservation_id: int | None = None,
    ) -> None:
        """
        同じ会議室で予約時間が重複していないことを非同期で確認する。

        Args:
            db: SQLAlchemyの非同期DBセッション。
            meeting_room_id: 確認対象の会議室ID。
            start_at: 予約開始日時。
            end_at: 予約終了日時。
            exclude_reservation_id: 更新時に重複判定から除外する予約ID。

        Raises:
            HTTPException: 同じ会議室で時間帯が重複する予約が存在する場合。
        """
        exists_overlap = await ReservationRepository.exists_overlapping_reservation(
            db=db,
            meeting_room_id=meeting_room_id,
            start_at=start_at,
            end_at=end_at,
            exclude_reservation_id=exclude_reservation_id,
        )

        if exists_overlap:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Reservation time overlaps with an existing reservation",
            )

    @staticmethod
    async def create_reservation(
        db: AsyncSession,
        reservation_create: ReservationCreateRequest,
    ) -> Reservation:
        """
        新規予約を非同期で登録する。

        ユーザー・会議室の有効性と予約時間の重複を確認したうえで登録する。

        Args:
            db: SQLAlchemyの非同期DBセッション。
            reservation_create: 予約登録リクエスト。

        Returns:
            登録された予約情報。
        """
        await ReservationService.validate_user(
            db=db,
            user_id=reservation_create.user_id,
        )
        await ReservationService.validate_meeting_room(
            db=db,
            meeting_room_id=reservation_create.meeting_room_id,
        )
        await ReservationService.validate_no_overlap(
            db=db,
            meeting_room_id=reservation_create.meeting_room_id,
            start_at=reservation_create.start_at,
            end_at=reservation_create.end_at,
        )

        return await ReservationRepository.create(
            db=db,
            reservation_create=reservation_create,
        )

    @staticmethod
    async def update_reservation(
        db: AsyncSession,
        reservation_id: int,
        reservation_update: ReservationUpdateRequest,
    ) -> Reservation:
        """
        指定されたIDの予約情報を非同期で更新する。

        予約の存在確認、ユーザー・会議室の有効性確認、
        予約時間の重複確認を行ったうえで更新する。

        Args:
            db: SQLAlchemyの非同期DBセッション。
            reservation_id: 更新対象の予約ID。
            reservation_update: 予約更新リクエスト。

        Returns:
            更新後の予約情報。
        """
        reservation = await ReservationService.get_reservation(
            db=db,
            reservation_id=reservation_id,
        )

        await ReservationService.validate_user(
            db=db,
            user_id=reservation_update.user_id,
        )
        await ReservationService.validate_meeting_room(
            db=db,
            meeting_room_id=reservation_update.meeting_room_id,
        )
        await ReservationService.validate_no_overlap(
            db=db,
            meeting_room_id=reservation_update.meeting_room_id,
            start_at=reservation_update.start_at,
            end_at=reservation_update.end_at,
            exclude_reservation_id=reservation_id,
        )

        return await ReservationRepository.update(
            db=db,
            reservation=reservation,
            reservation_update=reservation_update,
        )

    @staticmethod
    async def deactivate_reservation(
        db: AsyncSession,
        reservation_id: int,
    ) -> Reservation:
        """
        指定されたIDの予約を非同期で無効化する。

        物理削除ではなくis_activeをFalseに更新する。
        既に無効化されている予約の場合は409エラーを返す。

        Args:
            db: SQLAlchemyの非同期DBセッション。
            reservation_id: 無効化対象の予約ID。

        Returns:
            無効化後の予約情報。

        Raises:
            HTTPException: 予約が存在しない場合、または既に無効化済みの場合。
        """
        reservation = await ReservationService.get_reservation(
            db=db,
            reservation_id=reservation_id,
        )

        if not reservation.is_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Reservation is already inactive",
            )

        return await ReservationRepository.deactivate(
            db=db,
            reservation=reservation,
        )