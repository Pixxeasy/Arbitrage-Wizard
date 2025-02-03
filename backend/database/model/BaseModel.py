from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column, Mapped, MappedAsDataclass
from sqlalchemy import String
import uuid
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from sqlalchemy import Column, Integer
import datetime as dt


Base = declarative_base()

class BaseDBO(Base):
    __abstract__ = True

    guid: Mapped[str] = mapped_column(String(100), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)


class TimestampMixin:
    @declared_attr
    def created_at(cls):
        return Column(Integer, default=lambda: int(dt.datetime.now(dt.UTC).timestamp()), nullable=False)

