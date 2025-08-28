import datetime as dt
import uuid

from sqlalchemy import Column, Integer
from sqlalchemy import String
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from sqlalchemy.orm import mapped_column, Mapped

Base = declarative_base()


class BaseDBO(Base):
    __abstract__ = True

    guid: Mapped[str] = mapped_column(String(100), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)


class TimestampMixin:
    @declared_attr
    def created_at(self):
        return Column(Integer, default=lambda: int(dt.datetime.now(dt.UTC).timestamp()), nullable=False)
