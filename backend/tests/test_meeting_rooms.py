from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.db.session import AsyncSessionLocal
from app.main import app
from app.models.meeting_room import MeetingRoom


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


def unique_room_name(prefix: str) -> str:
    """
    テストごとに重複しない会議室名を生成する。

    同じ開発用DBを使ってテストを複数回実行しても、
    会議室名の一意制約により失敗しないようにする。
    """
    return f"{prefix}-{uuid4()}"


async def create_meeting_room_for_test(
    client: AsyncClient,
    headers: dict[str, str],
    created_meeting_room_ids: list[int],
    name_prefix: str = "テスト会議室",
) -> dict:
    """
    テスト用の会議室を作成する。

    Args:
        client: テスト用HTTPクライアント。
        headers: 認証済みリクエスト用ヘッダー。
        created_meeting_room_ids: 後処理で削除する会議室IDのリスト。
        name_prefix: 会議室名の接頭辞。

    Returns:
        作成された会議室レスポンス。
    """
    response = await client.post(
        "/api/v1/meeting-rooms",
        headers=headers,
        json={
            "name": unique_room_name(name_prefix),
            "capacity": 8,
            "location": "5F",
        },
    )

    assert response.status_code == 201

    data = response.json()
    created_meeting_room_ids.append(data["id"])

    return data


async def test_get_meeting_rooms_with_admin(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
) -> None:
    """
    管理者ユーザーで会議室一覧APIが正常にレスポンスを返すことを確認する。
    """
    response = await client.get(
        "/api/v1/meeting-rooms",
        headers=admin_auth_headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_get_meeting_rooms_with_user(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
) -> None:
    """
    一般ユーザーで会議室一覧APIが正常にレスポンスを返すことを確認する。
    """
    response = await client.get(
        "/api/v1/meeting-rooms",
        headers=user_auth_headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_get_meeting_rooms_without_auth(client: AsyncClient) -> None:
    """
    未認証で会議室一覧APIを実行した場合、
    401 Unauthorized が返ることを確認する。
    """
    response = await client.get("/api/v1/meeting-rooms")

    assert response.status_code == 401


async def test_create_meeting_room_with_admin(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    created_meeting_room_ids: list[int],
) -> None:
    """
    管理者ユーザーで会議室登録APIを実行し、
    新規会議室を作成できることを確認する。
    """
    room_name = unique_room_name("テスト会議室")

    response = await client.post(
        "/api/v1/meeting-rooms",
        headers=admin_auth_headers,
        json={
            "name": room_name,
            "capacity": 8,
            "location": "5F",
        },
    )

    assert response.status_code == 201

    data = response.json()
    created_meeting_room_ids.append(data["id"])

    assert data["name"] == room_name
    assert data["capacity"] == 8
    assert data["location"] == "5F"
    assert data["is_active"] is True


async def test_create_meeting_room_with_user_returns_403(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
) -> None:
    """
    一般ユーザーで会議室登録APIを実行した場合、
    403 Forbidden が返ることを確認する。
    """
    response = await client.post(
        "/api/v1/meeting-rooms",
        headers=user_auth_headers,
        json={
            "name": unique_room_name("一般ユーザー登録不可会議室"),
            "capacity": 6,
            "location": "6F",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin permission required"


async def test_create_meeting_room_with_duplicate_name(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    created_meeting_room_ids: list[int],
) -> None:
    """
    管理者ユーザーで既に存在する会議室名を登録しようとした場合、
    409 Conflict が返ることを確認する。
    """
    room_name = unique_room_name("重複テスト会議室")

    payload = {
        "name": room_name,
        "capacity": 6,
        "location": "6F",
    }

    first_response = await client.post(
        "/api/v1/meeting-rooms",
        headers=admin_auth_headers,
        json=payload,
    )

    assert first_response.status_code == 201

    created_meeting_room_ids.append(first_response.json()["id"])

    second_response = await client.post(
        "/api/v1/meeting-rooms",
        headers=admin_auth_headers,
        json=payload,
    )

    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Meeting room name already exists"


async def test_get_meeting_room_not_found(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
) -> None:
    """
    存在しない会議室IDを指定した場合、
    404 Not Found が返ることを確認する。
    """
    response = await client.get(
        "/api/v1/meeting-rooms/999999",
        headers=admin_auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Meeting room not found"


async def test_update_meeting_room_with_admin(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    created_meeting_room_ids: list[int],
) -> None:
    """
    管理者ユーザーで会議室更新APIを実行し、
    会議室情報を更新できることを確認する。
    """
    created_room = await create_meeting_room_for_test(
        client=client,
        headers=admin_auth_headers,
        created_meeting_room_ids=created_meeting_room_ids,
        name_prefix="更新前会議室",
    )

    meeting_room_id = created_room["id"]
    updated_room_name = unique_room_name("更新後会議室")

    update_response = await client.put(
        f"/api/v1/meeting-rooms/{meeting_room_id}",
        headers=admin_auth_headers,
        json={
            "name": updated_room_name,
            "capacity": 10,
            "location": "3F",
            "is_active": True,
        },
    )

    assert update_response.status_code == 200

    data = update_response.json()
    assert data["id"] == meeting_room_id
    assert data["name"] == updated_room_name
    assert data["capacity"] == 10
    assert data["location"] == "3F"
    assert data["is_active"] is True


async def test_update_meeting_room_with_user_returns_403(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    user_auth_headers: dict[str, str],
    created_meeting_room_ids: list[int],
) -> None:
    """
    一般ユーザーで会議室更新APIを実行した場合、
    403 Forbidden が返ることを確認する。
    """
    created_room = await create_meeting_room_for_test(
        client=client,
        headers=admin_auth_headers,
        created_meeting_room_ids=created_meeting_room_ids,
        name_prefix="一般ユーザー更新不可会議室",
    )

    response = await client.put(
        f"/api/v1/meeting-rooms/{created_room['id']}",
        headers=user_auth_headers,
        json={
            "name": unique_room_name("更新不可"),
            "capacity": 10,
            "location": "3F",
            "is_active": True,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin permission required"


async def test_deactivate_meeting_room_with_admin(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    created_meeting_room_ids: list[int],
) -> None:
    """
    管理者ユーザーで会議室無効化APIを実行し、
    is_active が false に更新されることを確認する。
    """
    created_room = await create_meeting_room_for_test(
        client=client,
        headers=admin_auth_headers,
        created_meeting_room_ids=created_meeting_room_ids,
        name_prefix="無効化テスト会議室",
    )

    meeting_room_id = created_room["id"]

    delete_response = await client.delete(
        f"/api/v1/meeting-rooms/{meeting_room_id}",
        headers=admin_auth_headers,
    )

    assert delete_response.status_code == 200

    data = delete_response.json()
    assert data["id"] == meeting_room_id
    assert data["is_active"] is False


async def test_deactivate_meeting_room_with_user_returns_403(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    user_auth_headers: dict[str, str],
    created_meeting_room_ids: list[int],
) -> None:
    """
    一般ユーザーで会議室無効化APIを実行した場合、
    403 Forbidden が返ることを確認する。
    """
    created_room = await create_meeting_room_for_test(
        client=client,
        headers=admin_auth_headers,
        created_meeting_room_ids=created_meeting_room_ids,
        name_prefix="一般ユーザー無効化不可会議室",
    )

    response = await client.delete(
        f"/api/v1/meeting-rooms/{created_room['id']}",
        headers=user_auth_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin permission required"


async def test_deactivate_inactive_meeting_room(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    created_meeting_room_ids: list[int],
) -> None:
    """
    管理者ユーザーで既に無効化済みの会議室を再度無効化しようとした場合、
    409 Conflict が返ることを確認する。
    """
    created_room = await create_meeting_room_for_test(
        client=client,
        headers=admin_auth_headers,
        created_meeting_room_ids=created_meeting_room_ids,
        name_prefix="再無効化テスト会議室",
    )

    meeting_room_id = created_room["id"]

    first_delete_response = await client.delete(
        f"/api/v1/meeting-rooms/{meeting_room_id}",
        headers=admin_auth_headers,
    )

    assert first_delete_response.status_code == 200

    second_delete_response = await client.delete(
        f"/api/v1/meeting-rooms/{meeting_room_id}",
        headers=admin_auth_headers,
    )

    assert second_delete_response.status_code == 409
    assert second_delete_response.json()["detail"] == "Meeting room is already inactive"