from sqlalchemy import MetaData
from sqlalchemy.orm import as_declarative, declared_attr

from src.common.configuration import conf

metadata = MetaData(
    naming_convention=conf.postgres.convention,
)


@as_declarative(metadata=metadata)
class Base:
    """Базовый класс SQLAlchemy-моделей с naming convention."""

    @classmethod
    @declared_attr
    def __tablename__(cls):
        """Возвращает имя таблицы по имени модели."""
        return cls.__name__.lower()

    __allow_unmapped__ = False
