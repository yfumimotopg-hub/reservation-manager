from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreateRequest


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
    def create_initial_users(db: Session) -> None:
        """
        開発環境用の初期ユーザーデータを作成する。

        ユーザー一覧APIの動作確認をしやすくするため、
        初回起動時にサンプルユーザーを登録する。
        """
        UserRepository.create_initial_users(db)