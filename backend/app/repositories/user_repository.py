from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreateRequest, UserUpdateRequest


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
    def find_by_id(db: Session, user_id: int) -> User | None:
        """
        ユーザーIDを条件にユーザーを1件取得する。

        Args:
            db: SQLAlchemyのDBセッション。
            user_id: 検索対象のユーザーID。

        Returns:
            該当するユーザー。存在しない場合はNone。
        """
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def find_by_email(db: Session, email: str) -> User | None:
        """
        メールアドレスを条件にユーザーを1件取得する。

        Args:
            db: SQLAlchemyのDBセッション。
            email: 検索対象のメールアドレス。

        Returns:
            該当するユーザー。存在しない場合はNone。
        """
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def create(db: Session, user_create: UserCreateRequest) -> User:
        """
        新規ユーザーを登録する。

        Args:
            db: SQLAlchemyのDBセッション。
            user_create: ユーザー登録リクエスト。

        Returns:
            登録されたユーザー情報。
        """
        user = User(
            name=user_create.name,
            email=user_create.email,
            role=user_create.role,
            is_active=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def update(
        db: Session,
        user: User,
        user_update: UserUpdateRequest,
    ) -> User:
        """
        既存ユーザー情報を更新する。

        Args:
            db: SQLAlchemyのDBセッション。
            user: 更新対象のユーザー。
            user_update: ユーザー更新リクエスト。

        Returns:
            更新後のユーザー情報。
        """
        user.name = user_update.name
        user.email = user_update.email
        user.role = user_update.role
        user.is_active = user_update.is_active

        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def deactivate(db: Session, user: User) -> User:
        """
        ユーザーを無効化する。

        物理削除は行わず、is_activeをFalseに更新することで
        過去データとの紐づきを維持する。

        Args:
            db: SQLAlchemyのDBセッション。
            user: 無効化対象のユーザー。

        Returns:
            無効化後のユーザー情報。
        """
        user.is_active = False

        db.commit()
        db.refresh(user)

        return user

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