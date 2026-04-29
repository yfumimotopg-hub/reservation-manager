from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.reservation import (
    ReservationCreateRequest,
    ReservationResponse,
    ReservationUpdateRequest,
)
from app.services.reservation_service import ReservationService

router = APIRouter()


@router.get("", response_model=list[ReservationResponse])
def get_reservations(
    db: Session = Depends(get_db),
) -> list[ReservationResponse]:
    """
    予約一覧を取得するAPIエンドポイント。

    DBに登録されている予約情報を一覧で返却する。
    """
    return ReservationService.get_reservations(db)


@router.get("/{reservation_id}", response_model=ReservationResponse)
def get_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
) -> ReservationResponse:
    """
    予約詳細を取得するAPIエンドポイント。

    パスパラメータで指定された予約IDに該当する予約情報を返却する。
    """
    return ReservationService.get_reservation(
        db=db,
        reservation_id=reservation_id,
    )


@router.post(
    "",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_reservation(
    reservation_create: ReservationCreateRequest,
    db: Session = Depends(get_db),
) -> ReservationResponse:
    """
    新規予約を登録するAPIエンドポイント。

    リクエスト内容をもとに予約を作成し、
    登録された予約情報を返却する。
    """
    return ReservationService.create_reservation(
        db=db,
        reservation_create=reservation_create,
    )


@router.put("/{reservation_id}", response_model=ReservationResponse)
def update_reservation(
    reservation_id: int,
    reservation_update: ReservationUpdateRequest,
    db: Session = Depends(get_db),
) -> ReservationResponse:
    """
    予約情報を更新するAPIエンドポイント。

    パスパラメータで指定された予約IDの予約情報を、
    リクエスト内容で更新する。
    """
    return ReservationService.update_reservation(
        db=db,
        reservation_id=reservation_id,
        reservation_update=reservation_update,
    )


@router.delete("/{reservation_id}", response_model=ReservationResponse)
def deactivate_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
) -> ReservationResponse:
    """
    予約を無効化するAPIエンドポイント。

    DBから物理削除せず、is_activeをFalseに更新する。
    """
    return ReservationService.deactivate_reservation(
        db=db,
        reservation_id=reservation_id,
    )