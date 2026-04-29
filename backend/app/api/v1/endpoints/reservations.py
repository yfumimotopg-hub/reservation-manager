from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.reservation import (
    ReservationCreateRequest,
    ReservationResponse,
    ReservationUpdateRequest,
)
from app.services.reservation_service import ReservationService

router = APIRouter()


@router.get("", response_model=list[ReservationResponse])
async def get_reservations(
    db: AsyncSession = Depends(get_db),
) -> list[ReservationResponse]:
    """
    予約一覧を取得するAPIエンドポイント。

    DBに登録されている予約情報を非同期で一覧取得して返却する。
    """
    return await ReservationService.get_reservations(db)


@router.get("/{reservation_id}", response_model=ReservationResponse)
async def get_reservation(
    reservation_id: int,
    db: AsyncSession = Depends(get_db),
) -> ReservationResponse:
    """
    予約詳細を取得するAPIエンドポイント。

    パスパラメータで指定された予約IDに該当する予約情報を非同期で返却する。
    """
    return await ReservationService.get_reservation(
        db=db,
        reservation_id=reservation_id,
    )


@router.post(
    "",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_reservation(
    reservation_create: ReservationCreateRequest,
    db: AsyncSession = Depends(get_db),
) -> ReservationResponse:
    """
    新規予約を登録するAPIエンドポイント。

    リクエスト内容をもとに予約を非同期で作成し、
    登録された予約情報を返却する。
    """
    return await ReservationService.create_reservation(
        db=db,
        reservation_create=reservation_create,
    )


@router.put("/{reservation_id}", response_model=ReservationResponse)
async def update_reservation(
    reservation_id: int,
    reservation_update: ReservationUpdateRequest,
    db: AsyncSession = Depends(get_db),
) -> ReservationResponse:
    """
    予約情報を更新するAPIエンドポイント。

    パスパラメータで指定された予約IDの予約情報を、
    リクエスト内容で非同期更新する。
    """
    return await ReservationService.update_reservation(
        db=db,
        reservation_id=reservation_id,
        reservation_update=reservation_update,
    )


@router.delete("/{reservation_id}", response_model=ReservationResponse)
async def deactivate_reservation(
    reservation_id: int,
    db: AsyncSession = Depends(get_db),
) -> ReservationResponse:
    """
    予約を無効化するAPIエンドポイント。

    DBから物理削除せず、is_activeをFalseに非同期で更新する。
    """
    return await ReservationService.deactivate_reservation(
        db=db,
        reservation_id=reservation_id,
    )