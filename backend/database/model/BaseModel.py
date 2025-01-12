from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column, Mapped, MappedAsDataclass
import uuid
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from sqlalchemy import Column, Integer
from datetime import datetime


Base = declarative_base()

class BaseDBO(Base):
    __abstract__ = True

    guid: Mapped[str] = mapped_column('guid', primary_key=True, default=lambda: str(uuid.uuid4()))


class TimestampMixin:
    @declared_attr
    def created_at(cls):
        return Column(Integer, default=lambda: datetime.utcnow().timestamp(), nullable=False)

