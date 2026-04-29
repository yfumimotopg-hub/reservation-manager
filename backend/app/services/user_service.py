from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreateRequest, UserUpdateRequest


class UserService:
    """
    ユーザー情報に関する業務処理を担当するサービス。

    API層から呼び出され、必要に応じてリポジトリを利用して
    ユーザー情報を非同期で扱う。
    """

    @staticmethod
    async def get_users(db: AsyncSession) -> list[User]:
        """
        ユーザー一覧を非同期で取得する。

        Args:
            db: SQLAlchemyの非同期DBセッション。

        Returns:
            ユーザー情報の一覧。
        """
        return await UserRepository.find_all(db)

    @staticmethod
    async def get_user(db: AsyncSession, user_id: int) -> User:
        """
        指定されたIDのユーザーを非同期で取得する。

        ユーザーが存在しない場合は404エラーを返す。

        Args:
            db: SQLAlchemyの非同期DBセッション。
            user_id: 取得対象のユーザーID。

        Returns:
            ユーザー情報。

        Raises:
            HTTPException: ユーザーが存在しない場合。
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

        return user

    @staticmethod
    async def create_user(
        db: AsyncSession,
        user_create: UserCreateRequest,
    ) -> User:
        """
        新規ユーザーを非同期で登録する。

        メールアドレスの重複を確認し、既に登録済みの場合は409エラーを返す。

        Args:
            db: SQLAlchemyの非同期DBセッション。
            user_create: ユーザー登録リクエスト。

        Returns:
            登録されたユーザー情報。

        Raises:
            HTTPException: メールアドレスが既に使用されている場合。
        """
        existing_user = await UserRepository.find_by_email(
            db=db,
            email=user_create.email,
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists",
            )

        return await UserRepository.create(
            db=db,
            user_create=user_create,
        )

    @staticmethod
    async def update_user(
        db: AsyncSession,
        user_id: int,
        user_update: UserUpdateRequest,
    ) -> User:
        """
        指定されたIDのユーザー情報を非同期で更新する。

        更新対象ユーザーの存在確認と、メールアドレスの重複確認を行ったうえで更新する。

        Args:
            db: SQLAlchemyの非同期DBセッション。
            user_id: 更新対象のユーザーID。
            user_update: ユーザー更新リクエスト。

        Returns:
            更新後のユーザー情報。

        Raises:
            HTTPException: ユーザーが存在しない場合、またはメールアドレスが重複している場合。
        """
        user = await UserService.get_user(
            db=db,
            user_id=user_id,
        )

        existing_user = await UserRepository.find_by_email(
            db=db,
            email=user_update.email,
        )

        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists",
            )

        return await UserRepository.update(
            db=db,
            user=user,
            user_update=user_update,
        )

    @staticmethod
    async def deactivate_user(db: AsyncSession, user_id: int) -> User:
        """
        指定されたIDのユーザーを非同期で無効化する。

        物理削除ではなくis_activeをFalseに更新する。
        既に無効化されているユーザーの場合は409エラーを返す。

        Args:
            db: SQLAlchemyの非同期DBセッション。
            user_id: 無効化対象のユーザーID。

        Returns:
            無効化後のユーザー情報。

        Raises:
            HTTPException: ユーザーが存在しない場合、または既に無効化済みの場合。
        """
        user = await UserService.get_user(
            db=db,
            user_id=user_id,
        )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User is already inactive",
            )

        return await UserRepository.deactivate(
            db=db,
            user=user,
        )

    @staticmethod
    async def create_initial_users(db: AsyncSession) -> None:
        """
        開発環境用の初期ユーザーデータを非同期で作成する。

        ユーザー一覧APIの動作確認をしやすくするため、
        初回起動時にサンプルユーザーを登録する。
        """
        await UserRepository.create_initial_users(db)