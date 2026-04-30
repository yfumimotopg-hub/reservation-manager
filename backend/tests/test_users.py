from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.db.session import AsyncSessionLocal
from app.main import app
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
        await db.execute(
            delete(User).where(User.id.in_(user_ids))
        )
        await db.commit()


def unique_email(prefix: str = "test-user") -> str:
    """
    テストごとに重複しないメールアドレスを生成する。

    同じ開発用DBを使ってテストを複数回実行しても、
    メールアドレスの一意制約により失敗しないようにする。
    """
    return f"{prefix}-{uuid4()}@example.com"


def unique_user_name(prefix: str = "Test User") -> str:
    """
    テストごとに重複しないユーザー名を生成する。

    Args:
        prefix: ユーザー名の接頭辞。

    Returns:
        UUID付きの一意なユーザー名。
    """
    return f"{prefix}-{uuid4()}"


async def create_user_for_test(
    client: AsyncClient,
    headers: dict[str, str],
    created_user_ids: list[int],
    name_prefix: str = "Test User",
    role: str = "user",
) -> dict:
    """
    テスト用のユーザーを作成する。

    Args:
        client: テスト用HTTPクライアント。
        headers: 認証済みリクエスト用ヘッダー。
        created_user_ids: 後処理で削除するユーザーIDのリスト。
        name_prefix: ユーザー名の接頭辞。
        role: 作成するユーザーの権限。

    Returns:
        作成されたユーザーレスポンス。
    """
    response = await client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "name": unique_user_name(name_prefix),
            "email": unique_email(),
            "role": role,
        },
    )

    assert response.status_code == 201

    data = response.json()
    created_user_ids.append(data["id"])

    return data


async def test_get_users_with_admin(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
) -> None:
    """
    管理者ユーザーでユーザー一覧APIを実行できることを確認する。
    """
    response = await client.get(
        "/api/v1/users",
        headers=admin_auth_headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_get_users_with_user_returns_403(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
) -> None:
    """
    一般ユーザーでユーザー一覧APIを実行した場合、
    403 Forbidden が返ることを確認する。
    """
    response = await client.get(
        "/api/v1/users",
        headers=user_auth_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin permission required"


async def test_get_users_without_auth_returns_401(
    client: AsyncClient,
) -> None:
    """
    未認証でユーザー一覧APIを実行した場合、
    401 Unauthorized が返ることを確認する。
    """
    response = await client.get("/api/v1/users")

    assert response.status_code == 401


async def test_get_user_with_admin(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
) -> None:
    """
    管理者ユーザーでユーザー詳細APIを実行できることを確認する。
    """
    response = await client.get(
        "/api/v1/users/1",
        headers=admin_auth_headers,
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == 1
    assert data["email"] == "admin@example.com"
    assert data["role"] == "admin"


async def test_get_user_with_user_returns_403(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
) -> None:
    """
    一般ユーザーでユーザー詳細APIを実行した場合、
    403 Forbidden が返ることを確認する。
    """
    response = await client.get(
        "/api/v1/users/1",
        headers=user_auth_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin permission required"


async def test_create_user_with_admin(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    created_user_ids: list[int],
) -> None:
    """
    管理者ユーザーでユーザー登録APIを実行し、
    新規ユーザーを作成できることを確認する。
    """
    name = unique_user_name()
    email = unique_email()

    response = await client.post(
        "/api/v1/users",
        headers=admin_auth_headers,
        json={
            "name": name,
            "email": email,
            "role": "user",
        },
    )

    assert response.status_code == 201

    data = response.json()
    created_user_ids.append(data["id"])

    assert data["name"] == name
    assert data["email"] == email
    assert data["role"] == "user"
    assert data["is_active"] is True


async def test_create_user_with_user_returns_403(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
) -> None:
    """
    一般ユーザーでユーザー登録APIを実行した場合、
    403 Forbidden が返ることを確認する。
    """
    response = await client.post(
        "/api/v1/users",
        headers=user_auth_headers,
        json={
            "name": unique_user_name(),
            "email": unique_email(),
            "role": "user",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin permission required"


async def test_create_user_with_duplicate_email_returns_409(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    created_user_ids: list[int],
) -> None:
    """
    既に存在するメールアドレスでユーザー登録した場合、
    409 Conflict が返ることを確認する。
    """
    email = unique_email()

    first_response = await client.post(
        "/api/v1/users",
        headers=admin_auth_headers,
        json={
            "name": unique_user_name("Duplicate User"),
            "email": email,
            "role": "user",
        },
    )

    assert first_response.status_code == 201
    created_user_ids.append(first_response.json()["id"])

    second_response = await client.post(
        "/api/v1/users",
        headers=admin_auth_headers,
        json={
            "name": unique_user_name("Duplicate User"),
            "email": email,
            "role": "user",
        },
    )

    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Email already exists"


async def test_update_user_with_admin(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    created_user_ids: list[int],
) -> None:
    """
    管理者ユーザーでユーザー更新APIを実行し、
    ユーザー情報を更新できることを確認する。
    """
    created_user = await create_user_for_test(
        client=client,
        headers=admin_auth_headers,
        created_user_ids=created_user_ids,
        name_prefix="Update User",
    )

    updated_name = unique_user_name("Updated User")
    updated_email = unique_email("updated-user")

    response = await client.put(
        f"/api/v1/users/{created_user['id']}",
        headers=admin_auth_headers,
        json={
            "name": updated_name,
            "email": updated_email,
            "role": "admin",
            "is_active": True,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == created_user["id"]
    assert data["name"] == updated_name
    assert data["email"] == updated_email
    assert data["role"] == "admin"
    assert data["is_active"] is True


async def test_update_user_with_user_returns_403(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    user_auth_headers: dict[str, str],
    created_user_ids: list[int],
) -> None:
    """
    一般ユーザーでユーザー更新APIを実行した場合、
    403 Forbidden が返ることを確認する。
    """
    created_user = await create_user_for_test(
        client=client,
        headers=admin_auth_headers,
        created_user_ids=created_user_ids,
        name_prefix="User Update Forbidden",
    )

    response = await client.put(
        f"/api/v1/users/{created_user['id']}",
        headers=user_auth_headers,
        json={
            "name": unique_user_name("Forbidden Update"),
            "email": unique_email("forbidden-update"),
            "role": "user",
            "is_active": True,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin permission required"


async def test_deactivate_user_with_admin(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    created_user_ids: list[int],
) -> None:
    """
    管理者ユーザーでユーザー無効化APIを実行し、
    is_active が false に更新されることを確認する。
    """
    created_user = await create_user_for_test(
        client=client,
        headers=admin_auth_headers,
        created_user_ids=created_user_ids,
        name_prefix="Deactivate User",
    )

    response = await client.delete(
        f"/api/v1/users/{created_user['id']}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == created_user["id"]
    assert data["is_active"] is False


async def test_deactivate_user_with_user_returns_403(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    user_auth_headers: dict[str, str],
    created_user_ids: list[int],
) -> None:
    """
    一般ユーザーでユーザー無効化APIを実行した場合、
    403 Forbidden が返ることを確認する。
    """
    created_user = await create_user_for_test(
        client=client,
        headers=admin_auth_headers,
        created_user_ids=created_user_ids,
        name_prefix="Deactivate Forbidden User",
    )

    response = await client.delete(
        f"/api/v1/users/{created_user['id']}",
        headers=user_auth_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin permission required"
    