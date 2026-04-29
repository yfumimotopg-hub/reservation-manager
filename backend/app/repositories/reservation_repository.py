from datetime import datetime

from sqlalchemy.orm import Session

from app.models.reservation import Reservation
from app.schemas.reservation import (
    ReservationCreateRequest,
    ReservationUpdateRequest,
)


class ReservationRepository:
    """
    予約情報に関するDB操作を担当するリポジトリ。

    SQLAlchemyを使用した検索・登録・更新・無効化などの
    DBアクセス処理を集約する。
    """

    @staticmethod
    def find_all(db: Session) -> list[Reservation]:
        """
        登録されている全予約を取得する。

        Args:
            db: SQLAlchemyのDBセッション。

        Returns:
            予約情報の一覧。
        """
        return db.query(Reservation).order_by(Reservation.start_at).all()

    @staticmethod
    def find_by_id(db: Session, reservation_id: int) -> Reservation | None:
        """
        予約IDを条件に予約を1件取得する。

        Args:
            db: SQLAlchemyのDBセッション。
            reservation_id: 検索対象の予約ID。

        Returns:
            該当する予約。存在しない場合はNone。
        """
        return (
            db.query(Reservation)
            .filter(Reservation.id == reservation_id)
            .first()
        )

    @staticmethod
    def exists_overlapping_reservation(
        db: Session,
        meeting_room_id: int,
        start_at: datetime,
        end_at: datetime,
        exclude_reservation_id: int | None = None,
    ) -> bool:
        """
        指定した会議室・時間帯に重複する有効な予約が存在するか確認する。

        Args:
            db: SQLAlchemyのDBセッション。
            meeting_room_id: 確認対象の会議室ID。
            start_at: 予約開始日時。
            end_at: 予約終了日時。
            exclude_reservation_id: 更新時に重複判定から除外する予約ID。

        Returns:
            重複する予約が存在する場合はTrue。
        """
        query = db.query(Reservation).filter(
            Reservation.meeting_room_id == meeting_room_id,
            Reservation.is_active.is_(True),
            Reservation.start_at < end_at,
            Reservation.end_at > start_at,
        )

        if exclude_reservation_id is not None:
            query = query.filter(Reservation.id != exclude_reservation_id)

        return query.first() is not None

    @staticmethod
    def create(
        db: Session,
        reservation_create: ReservationCreateRequest,
    ) -> Reservation:
        """
        新規予約を登録する。

        Args:
            db: SQLAlchemyのDBセッション。
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
        db.commit()
        db.refresh(reservation)

        return reservation

    @staticmethod
    def update(
        db: Session,
        reservation: Reservation,
        reservation_update: ReservationUpdateRequest,
    ) -> Reservation:
        """
        既存予約情報を更新する。

        Args:
            db: SQLAlchemyのDBセッション。
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

        db.commit()
        db.refresh(reservation)

        return reservation

    @staticmethod
    def deactivate(db: Session, reservation: Reservation) -> Reservation:
        """
        予約を無効化する。

        物理削除は行わず、is_activeをFalseに更新することで、
        予約履歴をDB上に残す。

        Args:
            db: SQLAlchemyのDBセッション。
            reservation: 無効化対象の予約。

        Returns:
            無効化後の予約情報。
        """
        reservation.is_active = False

        db.commit()
        db.refresh(reservation)

        return reservation