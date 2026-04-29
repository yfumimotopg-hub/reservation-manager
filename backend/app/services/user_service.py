from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository


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
    def create_initial_users(db: Session) -> None:
        """
        開発環境用の初期ユーザーデータを作成する。

        ユーザー一覧APIの動作確認をしやすくするため、
        初回起動時にサンプルユーザーを登録する。
        """
        UserRepository.create_initial_users(db)