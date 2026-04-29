from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """
    ユーザー情報に関するDB操作を担当するリポジトリ。

    SQLAlchemyを使用した検索・登録・更新・削除などのDBアクセス処理を集約する。
    """

    @staticmethod
    def find_all(db: Session) -> list[User]:
        """
        登録されている全ユーザーを取得する。

        Args:
            db: SQLAlchemyのDBセッション。

        Returns:
            ユーザー情報の一覧。
        """
        return db.query(User).order_by(User.id).all()

    @staticmethod
    def create_initial_users(db: Session) -> None:
        """
        初期表示確認用のユーザーデータを作成する。

        ユーザーが1件も存在しない場合のみ、サンプルユーザーを登録する。
        """
        exists_user = db.query(User).first()

        if exists_user:
            return

        users = [
            User(
                name="Admin User",
                email="admin@example.com",
                role="admin",
                is_active=True,
            ),
            User(
                name="General User",
                email="user@example.com",
                role="user",
                is_active=True,
            ),
        ]

        db.add_all(users)
        db.commit()