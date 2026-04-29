from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    SQLAlchemyの全DBモデルが継承する基底クラス。

    各テーブル定義モデルはこのBaseを継承することで、
    SQLAlchemyがメタデータを管理できるようにする。
    """