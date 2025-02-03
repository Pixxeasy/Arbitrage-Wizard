from database.model.BaseModel import BaseDBO
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String


class ExchangeDBO(BaseDBO):
    __tablename__ = 'exchanges'

    name: Mapped[str] = mapped_column(String(100))
    config_key: Mapped[str] = mapped_column(String(3), index=True)
    active: Mapped[bool] = mapped_column(default=True)