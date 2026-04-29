from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreateRequest, UserUpdateRequest


class UserService:
    """
    ユーザー情報に関する業務処理を担当するサービス。

    API層から呼び出され、必要に応じてリポジトリを利用してユーザー情報を扱う。
    """

    @staticmethod
    def get_users(db: Session) -> list[User]:
        """
        ユーザー一覧を取得する。

        Args:
            db: SQLAlchemyのDBセッション。

        Returns:
            ユーザー情報の一覧。
        """
        return UserRepository.find_all(db)

    @staticmethod
    def get_user(db: Session, user_id: int) -> User:
        """
        指定されたIDのユーザーを取得する。

        ユーザーが存在しない場合は404エラーを返す。

        Args:
            db: SQLAlchemyのDBセッション。
            user_id: 取得対象のユーザーID。

        Returns:
            ユーザー情報。

        Raises:
            HTTPException: ユーザーが存在しない場合。
        """
        user = UserRepository.find_by_id(
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
    def create_user(db: Session, user_create: UserCreateRequest) -> User:
        """
        新規ユーザーを登録する。

        メールアドレスの重複を確認し、既に登録済みの場合は409エラーを返す。

        Args:
            db: SQLAlchemyのDBセッション。
            user_create: ユーザー登録リクエスト。

        Returns:
            登録されたユーザー情報。

        Raises:
            HTTPException: メールアドレスが既に使用されている場合。
        """
        existing_user = UserRepository.find_by_email(
            db=db,
            email=user_create.email,
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists",
            )

        return UserRepository.create(
            db=db,
            user_create=user_create,
        )

    @staticmethod
    def update_user(
        db: Session,
        user_id: int,
        user_update: UserUpdateRequest,
    ) -> User:
        """
        指定されたIDのユーザー情報を更新する。

        更新対象ユーザーの存在確認と、メールアドレスの重複確認を行ったうえで更新する。

        Args:
            db: SQLAlchemyのDBセッション。
            user_id: 更新対象のユーザーID。
            user_update: ユーザー更新リクエスト。

        Returns:
            更新後のユーザー情報。

        Raises:
            HTTPException: ユーザーが存在しない場合、またはメールアドレスが重複している場合。
        """
        user = UserService.get_user(
            db=db,
            user_id=user_id,
        )

        existing_user = UserRepository.find_by_email(
            db=db,
            email=user_update.email,
        )

        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists",
            )

        return UserRepository.update(
            db=db,
            user=user,
            user_update=user_update,
        )

    @staticmethod
    def deactivate_user(db: Session, user_id: int) -> User:
        """
        指定されたIDのユーザーを無効化する。

        物理削除ではなくis_activeをFalseに更新する。
        既に無効化されているユーザーの場合は409エラーを返す。

        Args:
            db: SQLAlchemyのDBセッション。
            user_id: 無効化対象のユーザーID。

        Returns:
            無効化後のユーザー情報。

        Raises:
            HTTPException: ユーザーが存在しない場合、または既に無効化済みの場合。
        """
        user = UserService.get_user(
            db=db,
            user_id=user_id,
        )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User is already inactive",
            )

        return UserRepository.deactivate(
            db=db,
            user=user,
        )

    @staticmethod
    def create_initial_users(db: Session) -> None:
        """
        開発環境用の初期ユーザーデータを作成する。

        ユーザー一覧APIの動作確認をしやすくするため、
        初回起動時にサンプルユーザーを登録する。
        """
        UserRepository.create_initial_users(db)