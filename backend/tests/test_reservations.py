from collections.abc import AsyncGenerator
from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.db.session import AsyncSessionLocal
from app.main import app
from app.models.meeting_room import MeetingRoom
from app.models.reservation import Reservation
from app.models.user import User


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    FastAPIアプリケーションに対して非同期リクエストを送るための
    テスト用HTTPクライアントを生成する。
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as async_client:
        yield async_client


@pytest.fixture
async def admin_auth_headers(client: AsyncClient) -> dict[str, str]:
    """
    管理者ユーザーでログインし、認証済みリクエスト用のヘッダーを生成する。

    Returns:
        Authorizationヘッダーを含む辞書。
    """
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": "password",
        },
    )

    assert response.status_code == 200

    access_token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {access_token}",
    }


@pytest.fixture
async def user_auth_headers(client: AsyncClient) -> dict[str, str]:
    """
    一般ユーザーでログインし、認証済みリクエスト用のヘッダーを生成する。

    Returns:
        Authorizationヘッダーを含む辞書。
    """
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "user@example.com",
            "password": "password",
        },
    )

    assert response.status_code == 200

    access_token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {access_token}",
    }


@pytest.fixture
async def created_user_ids() -> AsyncGenerator[list[int], None]:
    """
    テスト中に作成したユーザーIDを管理し、テスト終了後に物理削除する。

    アプリ本体では論理削除を採用しているが、
    テストデータは永続化する必要がないため、後処理でDBから削除する。
    """
    user_ids: list[int] = []

    yield user_ids

    if not user_ids:
        return

    async with AsyncSessionLocal() as db:
        await db.execute(delete(User).where(User.id.in_(user_ids)))
        await db.commit()


@pytest.fixture
async def created_meeting_room_ids() -> AsyncGenerator[list[int], None]:
    """
    テスト中に作成した会議室IDを管理し、テスト終了後に物理削除する。

    アプリ本体では論理削除を採用しているが、
    テストデータは永続化する必要がないため、後処理でDBから削除する。
    """
    meeting_room_ids: list[int] = []

    yield meeting_room_ids

    if not meeting_room_ids:
        return

    async with AsyncSessionLocal() as db:
        await db.execute(
            delete(MeetingRoom).where(MeetingRoom.id.in_(meeting_room_ids))
        )
        await db.commit()


@pytest.fixture
async def created_reservation_ids() -> AsyncGenerator[list[int], None]:
    """
    テスト中に作成した予約IDを管理し、テスト終了後に物理削除する。

    アプリ本体では論理削除を採用しているが、
    テストデータは永続化する必要がないため、後処理でDBから削除する。
    """
    reservation_ids: list[int] = []

    yield reservation_ids

    if not reservation_ids:
        return

    async with AsyncSessionLocal() as db:
        await db.execute(
            delete(Reservation).where(Reservation.id.in_(reservation_ids))
        )
        await db.commit()


def unique_email(prefix: str = "reservation-test-user") -> str:
    """
    テストごとに重複しないメールアドレスを生成する。

    Args:
        prefix: メールアドレスの接頭辞。

    Returns:
        UUID付きの一意なメールアドレス。
    """
    return f"{prefix}-{uuid4()}@example.com"


def unique_name(prefix: str) -> str:
    """
    テストごとに重複しない名称を生成する。

    Args:
        prefix: 名称の接頭辞。

    Returns:
        UUID付きの一意な名称。
    """
    return f"{prefix}-{uuid4()}"


def iso_datetime(base_hour: int = 10) -> tuple[str, str]:
    """
    テスト用の予約開始日時・終了日時を生成する。

    Args:
        base_hour: 予約開始時刻の時間。

    Returns:
        ISO形式の開始日時と終了日時。
    """
    start_at = datetime(2026, 5, 1, base_hour, 0, 0)
    end_at = start_at + timedelta(hours=1)

    return start_at.isoformat(), end_at.isoformat()


async def fetch_current_user_for_test(
    client: AsyncClient,
    headers: dict[str, str],
) -> dict:
    """
    テスト用にログイン中ユーザー情報を取得する。

    Args:
        client: テスト用HTTPクライアント。
        headers: 認証済みリクエスト用ヘッダー。

    Returns:
        ログイン中ユーザー情報。
    """
    response = await client.get(
        "/api/v1/auth/me",
        headers=headers,
    )

    assert response.status_code == 200

    return response.json()


async def create_user_for_test(
    client: AsyncClient,
    headers: dict[str, str],
    created_user_ids: list[int],
    is_active: bool = True,
) -> dict:
    """
    テスト用のユーザーを作成する。

    Args:
        client: テスト用HTTPクライアント。
        headers: 認証済みリクエスト用ヘッダー。
        created_user_ids: 後処理で削除するユーザーIDのリスト。
        is_active: 作成後のユーザー有効状態。

    Returns:
        作成されたユーザーレスポンス。
    """
    create_response = await client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "name": unique_name("Reservation Test User"),
            "email": unique_email(),
            "role": "user",
        },
    )

    assert create_response.status_code == 201

    user = create_response.json()
    created_user_ids.append(user["id"])

    if is_active:
        return user

    update_response = await client.put(
        f"/api/v1/users/{user['id']}",
        headers=headers,
        json={
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "is_active": False,
        },
    )

    assert update_response.status_code == 200

    return update_response.json()


async def create_meeting_room_for_test(
    client: AsyncClient,
    headers: dict[str, str],
    created_meeting_room_ids: list[int],
    is_active: bool = True,
) -> dict:
    """
    テスト用の会議室を作成する。

    Args:
        client: テスト用HTTPクライアント。
        headers: 認証済みリクエスト用ヘッダー。
        created_meeting_room_ids: 後処理で削除する会議室IDのリスト。
        is_active: 作成後の会議室有効状態。

    Returns:
        作成された会議室レスポンス。
    """
    create_response = await client.post(
        "/api/v1/meeting-rooms",
        headers=headers,
        json={
            "name": unique_name("予約テスト会議室"),
            "capacity": 8,
            "location": "5F",
        },
    )

    assert create_response.status_code == 201

    meeting_room = create_response.json()
    created_meeting_room_ids.append(meeting_room["id"])

    if is_active:
        return meeting_room

    update_response = await client.put(
        f"/api/v1/meeting-rooms/{meeting_room['id']}",
        headers=headers,
        json={
            "name": meeting_room["name"],
            "capacity": meeting_room["capacity"],
            "location": meeting_room["location"],
            "is_active": False,
        },
    )

    assert update_response.status_code == 200

    return update_response.json()


async def create_reservation_for_test(
    client: AsyncClient,
    headers: dict[str, str],
    created_reservation_ids: list[int],
    user_id: int,
    meeting_room_id: int,
    start_at: str,
    end_at: str,
    title_prefix: str = "予約テスト",
) -> dict:
    """
    テスト用の予約を作成する。

    Args:
        client: テスト用HTTPクライアント。
        headers: 認証済みリクエスト用ヘッダー。
        created_reservation_ids: 後処理で削除する予約IDのリスト。
        user_id: 予約者ユーザーID。
        meeting_room_id: 予約対象会議室ID。
        start_at: 予約開始日時。
        end_at: 予約終了日時。
        title_prefix: 予約タイトルの接頭辞。

    Returns:
        作成された予約レスポンス。
    """
    response = await client.post(
        "/api/v1/reservations",
        headers=headers,
        json={
            "user_id": user_id,
            "meeting_room_id": meeting_room_id,
            "title": unique_name(title_prefix),
            "start_at": start_at,
            "end_at": end_at,
        },
    )

    assert response.status_code == 201

    reservation = response.json()
    created_reservation_ids.append(reservation["id"])

    return reservation


async def test_create_reservation(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    created_user_ids: list[int],
    created_meeting_room_ids: list[int],
    created_reservation_ids: list[int],
) -> None:
    """
    予約登録APIで新規予約を作成できることを確認する。
    """
    user = await create_user_for_test(
        client=client,
        headers=admin_auth_headers,
        created_user_ids=created_user_ids,
    )
    meeting_room = await create_meeting_room_for_test(
        client=client,
        headers=admin_auth_headers,
        created_meeting_room_ids=created_meeting_room_ids,
    )
    start_at, end_at = iso_datetime(base_hour=10)

    response = await client.post(
        "/api/v1/reservations",
        headers=admin_auth_headers,
        json={
            "user_id": user["id"],
            "meeting_room_id": meeting_room["id"],
            "title": "開発定例",
            "start_at": start_at,
            "end_at": end_at,
        },
    )

    assert response.status_code == 201

    data = response.json()
    created_reservation_ids.append(data["id"])

    assert data["user_id"] == user["id"]
    assert data["meeting_room_id"] == meeting_room["id"]
    assert data["title"] == "開発定例"
    assert data["is_active"] is True


async def test_create_reservation_with_not_found_user_returns_404(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    created_meeting_room_ids: list[int],
) -> None:
    """
    存在しないユーザーIDで予約登録した場合、
    404 Not Found が返ることを確認する。
    """
    meeting_room = await create_meeting_room_for_test(
        client=client,
        headers=admin_auth_headers,
        created_meeting_room_ids=created_meeting_room_ids,
    )
    start_at, end_at = iso_datetime(base_hour=11)

    response = await client.post(
        "/api/v1/reservations",
        headers=admin_auth_headers,
        json={
            "user_id": 999999,
            "meeting_room_id": meeting_room["id"],
            "title": "存在しないユーザー",
            "start_at": start_at,
            "end_at": end_at,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


async def test_create_reservation_with_inactive_user_returns_409(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    created_user_ids: list[int],
    created_meeting_room_ids: list[int],
) -> None:
    """
    無効ユーザーで予約登録した場合、
    409 Conflict が返ることを確認する。
    """
    inactive_user = await create_user_for_test(
        client=client,
        headers=admin_auth_headers,
        created_user_ids=created_user_ids,
        is_active=False,
    )
    meeting_room = await create_meeting_room_for_test(
        client=client,
        headers=admin_auth_headers,
        created_meeting_room_ids=created_meeting_room_ids,
    )
    start_at, end_at = iso_datetime(base_hour=12)

    response = await client.post(
        "/api/v1/reservations",
        headers=admin_auth_headers,
        json={
            "user_id": inactive_user["id"],
            "meeting_room_id": meeting_room["id"],
            "title": "無効ユーザー予約",
            "start_at": start_at,
            "end_at": end_at,
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "User is inactive"


async def test_create_reservation_with_not_found_meeting_room_returns_404(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    created_user_ids: list[int],
) -> None:
    """
    存在しない会議室IDで予約登録した場合、
    404 Not Found が返ることを確認する。
    """
    user = await create_user_for_test(
        client=client,
        headers=admin_auth_headers,
        created_user_ids=created_user_ids,
    )
    start_at, end_at = iso_datetime(base_hour=13)

    response = await client.post(
        "/api/v1/reservations",
        headers=admin_auth_headers,
        json={
            "user_id": user["id"],
            "meeting_room_id": 999999,
            "title": "存在しない会議室",
            "start_at": start_at,
            "end_at": end_at,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Meeting room not found"


async def test_create_reservation_with_inactive_meeting_room_returns_409(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    created_user_ids: list[int],
    created_meeting_room_ids: list[int],
) -> None:
    """
    無効会議室で予約登録した場合、
    409 Conflict が返ることを確認する。
    """
    user = await create_user_for_test(
        client=client,
        headers=admin_auth_headers,
        created_user_ids=created_user_ids,
    )
    inactive_meeting_room = await create_meeting_room_for_test(
        client=client,
        headers=admin_auth_headers,
        created_meeting_room_ids=created_meeting_room_ids,
        is_active=False,
    )
    start_at, end_at = iso_datetime(base_hour=14)

    response = await client.post(
        "/api/v1/reservations",
        headers=admin_auth_headers,
        json={
            "user_id": user["id"],
            "meeting_room_id": inactive_meeting_room["id"],
            "title": "無効会議室予約",
            "start_at": start_at,
            "end_at": end_at,
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Meeting room is inactive"


async def test_create_reservation_with_invalid_time_range_returns_422(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    created_user_ids: list[int],
    created_meeting_room_ids: list[int],
) -> None:
    """
    開始日時が終了日時以降の場合、
    422 Unprocessable Entity が返ることを確認する。
    """
    user = await create_user_for_test(
        client=client,
        headers=admin_auth_headers,
        created_user_ids=created_user_ids,
    )
    meeting_room = await create_meeting_room_for_test(
        client=client,
        headers=admin_auth_headers,
        created_meeting_room_ids=created_meeting_room_ids,
    )

    response = await client.post(
        "/api/v1/reservations",
        headers=admin_auth_headers,
        json={
            "user_id": user["id"],
            "meeting_room_id": meeting_room["id"],
            "title": "不正な時間",
            "start_at": "2026-05-01T15:00:00",
            "end_at": "2026-05-01T15:00:00",
        },
    )

    assert response.status_code == 422


async def test_create_reservation_with_overlap_returns_409(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    created_user_ids: list[int],
    created_meeting_room_ids: list[int],
    created_reservation_ids: list[int],
) -> None:
    """
    同じ会議室で予約時間が重複する場合、
    409 Conflict が返ることを確認する。
    """
    user = await create_user_for_test(
        client=client,
        headers=admin_auth_headers,
        created_user_ids=created_user_ids,
    )
    meeting_room = await create_meeting_room_for_test(
        client=client,
        headers=admin_auth_headers,
        created_meeting_room_ids=created_meeting_room_ids,
    )

    await create_reservation_for_test(
        client=client,
        headers=admin_auth_headers,
        created_reservation_ids=created_reservation_ids,
        user_id=user["id"],
        meeting_room_id=meeting_room["id"],
        start_at="2026-05-02T10:00:00",
        end_at="2026-05-02T11:00:00",
        title_prefix="既存予約",
    )

    response = await client.post(
        "/api/v1/reservations",
        headers=admin_auth_headers,
        json={
            "user_id": user["id"],
            "meeting_room_id": meeting_room["id"],
            "title": "重複予約",
            "start_at": "2026-05-02T10:30:00",
            "end_at": "2026-05-02T11:30:00",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Reservation time overlaps with an existing reservation"
    )


async def test_create_reservation_with_adjacent_time_succeeds(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    created_user_ids: list[int],
    created_meeting_room_ids: list[int],
    created_reservation_ids: list[int],
) -> None:
    """
    既存予約の終了時刻と新規予約の開始時刻が同じ場合、
    重複扱いにならず登録できることを確認する。
    """
    user = await create_user_for_test(
        client=client,
        headers=admin_auth_headers,
        created_user_ids=created_user_ids,
    )
    meeting_room = await create_meeting_room_for_test(
        client=client,
        headers=admin_auth_headers,
        created_meeting_room_ids=created_meeting_room_ids,
    )

    await create_reservation_for_test(
        client=client,
        headers=admin_auth_headers,
        created_reservation_ids=created_reservation_ids,
        user_id=user["id"],
        meeting_room_id=meeting_room["id"],
        start_at="2026-05-03T10:00:00",
        end_at="2026-05-03T11:00:00",
        title_prefix="既存予約",
    )

    response = await client.post(
        "/api/v1/reservations",
        headers=admin_auth_headers,
        json={
            "user_id": user["id"],
            "meeting_room_id": meeting_room["id"],
            "title": "隣接予約",
            "start_at": "2026-05-03T11:00:00",
            "end_at": "2026-05-03T12:00:00",
        },
    )

    assert response.status_code == 201

    data = response.json()
    created_reservation_ids.append(data["id"])

    assert data["start_at"] == "2026-05-03T11:00:00"
    assert data["end_at"] == "2026-05-03T12:00:00"


async def test_deactivate_reservation(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    created_user_ids: list[int],
    created_meeting_room_ids: list[int],
    created_reservation_ids: list[int],
) -> None:
    """
    予約無効化APIで is_active が false に更新されることを確認する。
    """
    user = await create_user_for_test(
        client=client,
        headers=admin_auth_headers,
        created_user_ids=created_user_ids,
    )
    meeting_room = await create_meeting_room_for_test(
        client=client,
        headers=admin_auth_headers,
        created_meeting_room_ids=created_meeting_room_ids,
    )
    start_at, end_at = iso_datetime(base_hour=16)

    reservation = await create_reservation_for_test(
        client=client,
        headers=admin_auth_headers,
        created_reservation_ids=created_reservation_ids,
        user_id=user["id"],
        meeting_room_id=meeting_room["id"],
        start_at=start_at,
        end_at=end_at,
    )

    response = await client.delete(
        f"/api/v1/reservations/{reservation['id']}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == reservation["id"]
    assert data["is_active"] is False


async def test_deactivate_inactive_reservation_returns_409(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    created_user_ids: list[int],
    created_meeting_room_ids: list[int],
    created_reservation_ids: list[int],
) -> None:
    """
    既に無効化済みの予約を再度無効化しようとした場合、
    409 Conflict が返ることを確認する。
    """
    user = await create_user_for_test(
        client=client,
        headers=admin_auth_headers,
        created_user_ids=created_user_ids,
    )
    meeting_room = await create_meeting_room_for_test(
        client=client,
        headers=admin_auth_headers,
        created_meeting_room_ids=created_meeting_room_ids,
    )
    start_at, end_at = iso_datetime(base_hour=17)

    reservation = await create_reservation_for_test(
        client=client,
        headers=admin_auth_headers,
        created_reservation_ids=created_reservation_ids,
        user_id=user["id"],
        meeting_room_id=meeting_room["id"],
        start_at=start_at,
        end_at=end_at,
    )

    first_response = await client.delete(
        f"/api/v1/reservations/{reservation['id']}",
        headers=admin_auth_headers,
    )
    assert first_response.status_code == 200

    second_response = await client.delete(
        f"/api/v1/reservations/{reservation['id']}",
        headers=admin_auth_headers,
    )

    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Reservation is already inactive"


async def test_user_create_reservation_uses_current_user_id(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    user_auth_headers: dict[str, str],
    created_user_ids: list[int],
    created_meeting_room_ids: list[int],
    created_reservation_ids: list[int],
) -> None:
    """
    一般ユーザーで予約登録した場合、
    リクエストのuser_idが他人のIDでもログイン中ユーザーIDで登録されることを確認する。
    """
    current_user = await fetch_current_user_for_test(
        client=client,
        headers=user_auth_headers,
    )

    other_user = await create_user_for_test(
        client=client,
        headers=admin_auth_headers,
        created_user_ids=created_user_ids,
    )

    meeting_room = await create_meeting_room_for_test(
        client=client,
        headers=admin_auth_headers,
        created_meeting_room_ids=created_meeting_room_ids,
    )

    response = await client.post(
        "/api/v1/reservations",
        headers=user_auth_headers,
        json={
            "user_id": other_user["id"],
            "meeting_room_id": meeting_room["id"],
            "title": "一般ユーザー予約",
            "start_at": "2026-06-01T10:00:00",
            "end_at": "2026-06-01T11:00:00",
        },
    )

    assert response.status_code == 201

    reservation = response.json()
    created_reservation_ids.append(reservation["id"])

    assert reservation["user_id"] == current_user["id"]
    assert reservation["user_id"] != other_user["id"]


async def test_user_get_reservations_returns_only_own_reservations(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    user_auth_headers: dict[str, str],
    created_user_ids: list[int],
    created_meeting_room_ids: list[int],
    created_reservation_ids: list[int],
) -> None:
    """
    一般ユーザーで予約一覧APIを実行した場合、
    自分の予約のみ取得できることを確認する。
    """
    current_user = await fetch_current_user_for_test(
        client=client,
        headers=user_auth_headers,
    )

    other_user = await create_user_for_test(
        client=client,
        headers=admin_auth_headers,
        created_user_ids=created_user_ids,
    )

    meeting_room = await create_meeting_room_for_test(
        client=client,
        headers=admin_auth_headers,
        created_meeting_room_ids=created_meeting_room_ids,
    )

    own_reservation = await create_reservation_for_test(
        client=client,
        headers=admin_auth_headers,
        created_reservation_ids=created_reservation_ids,
        user_id=current_user["id"],
        meeting_room_id=meeting_room["id"],
        start_at="2026-06-02T10:00:00",
        end_at="2026-06-02T11:00:00",
        title_prefix="自分の予約",
    )

    other_reservation = await create_reservation_for_test(
        client=client,
        headers=admin_auth_headers,
        created_reservation_ids=created_reservation_ids,
        user_id=other_user["id"],
        meeting_room_id=meeting_room["id"],
        start_at="2026-06-02T11:00:00",
        end_at="2026-06-02T12:00:00",
        title_prefix="他人の予約",
    )

    response = await client.get(
        "/api/v1/reservations",
        headers=user_auth_headers,
    )

    assert response.status_code == 200

    reservation_ids = [reservation["id"] for reservation in response.json()]

    assert own_reservation["id"] in reservation_ids
    assert other_reservation["id"] not in reservation_ids


async def test_user_get_other_user_reservation_returns_403(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    user_auth_headers: dict[str, str],
    created_user_ids: list[int],
    created_meeting_room_ids: list[int],
    created_reservation_ids: list[int],
) -> None:
    """
    一般ユーザーで他人の予約詳細APIを実行した場合、
    403 Forbidden が返ることを確認する。
    """
    other_user = await create_user_for_test(
        client=client,
        headers=admin_auth_headers,
        created_user_ids=created_user_ids,
    )

    meeting_room = await create_meeting_room_for_test(
        client=client,
        headers=admin_auth_headers,
        created_meeting_room_ids=created_meeting_room_ids,
    )

    other_reservation = await create_reservation_for_test(
        client=client,
        headers=admin_auth_headers,
        created_reservation_ids=created_reservation_ids,
        user_id=other_user["id"],
        meeting_room_id=meeting_room["id"],
        start_at="2026-06-03T10:00:00",
        end_at="2026-06-03T11:00:00",
        title_prefix="他人の予約詳細",
    )

    response = await client.get(
        f"/api/v1/reservations/{other_reservation['id']}",
        headers=user_auth_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You can only operate your own reservations"


async def test_user_deactivate_other_user_reservation_returns_403(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    user_auth_headers: dict[str, str],
    created_user_ids: list[int],
    created_meeting_room_ids: list[int],
    created_reservation_ids: list[int],
) -> None:
    """
    一般ユーザーで他人の予約を無効化しようとした場合、
    403 Forbidden が返ることを確認する。
    """
    other_user = await create_user_for_test(
        client=client,
        headers=admin_auth_headers,
        created_user_ids=created_user_ids,
    )

    meeting_room = await create_meeting_room_for_test(
        client=client,
        headers=admin_auth_headers,
        created_meeting_room_ids=created_meeting_room_ids,
    )

    other_reservation = await create_reservation_for_test(
        client=client,
        headers=admin_auth_headers,
        created_reservation_ids=created_reservation_ids,
        user_id=other_user["id"],
        meeting_room_id=meeting_room["id"],
        start_at="2026-06-04T10:00:00",
        end_at="2026-06-04T11:00:00",
        title_prefix="他人の無効化不可予約",
    )

    response = await client.delete(
        f"/api/v1/reservations/{other_reservation['id']}",
        headers=user_auth_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You can only operate your own reservations"


async def test_admin_deactivate_other_user_reservation_succeeds(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    created_user_ids: list[int],
    created_meeting_room_ids: list[int],
    created_reservation_ids: list[int],
) -> None:
    """
    管理者ユーザーで他人の予約を無効化できることを確認する。
    """
    other_user = await create_user_for_test(
        client=client,
        headers=admin_auth_headers,
        created_user_ids=created_user_ids,
    )

    meeting_room = await create_meeting_room_for_test(
        client=client,
        headers=admin_auth_headers,
        created_meeting_room_ids=created_meeting_room_ids,
    )

    reservation = await create_reservation_for_test(
        client=client,
        headers=admin_auth_headers,
        created_reservation_ids=created_reservation_ids,
        user_id=other_user["id"],
        meeting_room_id=meeting_room["id"],
        start_at="2026-06-05T10:00:00",
        end_at="2026-06-05T11:00:00",
        title_prefix="管理者無効化予約",
    )

    response = await client.delete(
        f"/api/v1/reservations/{reservation['id']}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == reservation["id"]
    assert data["is_active"] is False