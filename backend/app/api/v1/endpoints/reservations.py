from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
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
    current_user: User = Depends(get_current_user),
) -> list[ReservationResponse]:
    """
    予約一覧を取得するAPIエンドポイント。

    adminは全予約、userは自分の予約のみ返却する。
    """
    return await ReservationService.get_reservations(
        db=db,
        current_user=current_user,
    )


@router.get("/{reservation_id}", response_model=ReservationResponse)
async def get_reservation(
    reservation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReservationResponse:
    """
    予約詳細を取得するAPIエンドポイント。

    adminは全予約、userは自分の予約のみ取得できる。
    """
    return await ReservationService.get_reservation(
        db=db,
        reservation_id=reservation_id,
        current_user=current_user,
    )


@router.post(
    "",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_reservation(
    reservation_create: ReservationCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReservationResponse:
    """
    新規予約を登録するAPIエンドポイント。

    adminは任意のユーザーIDで予約登録できる。
    userはログイン中ユーザーIDで予約登録する。
    """
    return await ReservationService.create_reservation(
        db=db,
        reservation_create=reservation_create,
        current_user=current_user,
    )


@router.put("/{reservation_id}", response_model=ReservationResponse)
async def update_reservation(
    reservation_id: int,
    reservation_update: ReservationUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReservationResponse:
    """
    予約情報を更新するAPIエンドポイント。

    adminは全予約、userは自分の予約のみ更新できる。
    """
    return await ReservationService.update_reservation(
        db=db,
        reservation_id=reservation_id,
        reservation_update=reservation_update,
        current_user=current_user,
    )


@router.delete("/{reservation_id}", response_model=ReservationResponse)
async def deactivate_reservation(
    reservation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReservationResponse:
    """
    予約を無効化するAPIエンドポイント。

    adminは全予約、userは自分の予約のみ無効化できる。
    """
    return await ReservationService.deactivate_reservation(
        db=db,
        reservation_id=reservation_id,
        current_user=current_user,
    )