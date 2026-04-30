from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreateRequest, UserUpdateRequest


class UserRepository:
    """
    ユーザー情報に関するDB操作を担当するリポジトリ。

    SQLAlchemyのAsyncSessionを使用し、非同期で検索・登録・更新・無効化などの
    DBアクセス処理を行う。
    """

    @staticmethod
    async def find_all(db: AsyncSession) -> list[User]:
        """
        登録されている全ユーザーを非同期で取得する。
        """
        result = await db.execute(
            select(User).order_by(User.id)
        )
        return list(result.scalars().all())

    @staticmethod
    async def find_by_id(db: AsyncSession, user_id: int) -> User | None:
        """
        ユーザーIDを条件にユーザーを1件非同期で取得する。
        """
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def find_by_email(db: AsyncSession, email: str) -> User | None:
        """
        メールアドレスを条件にユーザーを1件非同期で取得する。
        """
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
        db: AsyncSession,
        user_create: UserCreateRequest,
    ) -> User:
        """
        新規ユーザーを非同期で登録する。

        初期パスワードは仮で password に設定する。
        後続対応でユーザー作成時にパスワードを受け取る形へ変更する想定。
        """
        user = User(
            name=user_create.name,
            email=user_create.email,
            password_hash=hash_password("password"),
            role=user_create.role,
            is_active=True,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def update(
        db: AsyncSession,
        user: User,
        user_update: UserUpdateRequest,
    ) -> User:
        """
        既存ユーザー情報を非同期で更新する。
        """
        user.name = user_update.name
        user.email = user_update.email
        user.role = user_update.role
        user.is_active = user_update.is_active

        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def deactivate(db: AsyncSession, user: User) -> User:
        """
        ユーザーを非同期で無効化する。
        """
        user.is_active = False

        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def create_initial_users(db: AsyncSession) -> None:
        """
        初期表示確認用のユーザーデータを非同期で作成する。

        ユーザーが1件も存在しない場合のみ、サンプルユーザーを登録する。
        """
        result = await db.execute(select(User).limit(1))
        exists_user = result.scalar_one_or_none()

        if exists_user:
            return

        users = [
            User(
                name="Admin User",
                email="admin@example.com",
                password_hash=hash_password("password"),
                role="admin",
                is_active=True,
            ),
            User(
                name="General User",
                email="user@example.com",
                password_hash=hash_password("password"),
                role="user",
                is_active=True,
            ),
        ]

        db.add_all(users)
        await db.commit()