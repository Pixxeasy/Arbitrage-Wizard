from database.model.BaseModel import BaseDBO
from sqlalchemy.orm import Mapped, mapped_column


class ExchangeDBO(BaseDBO):
    __tablename__ = 'exchanges'

    name: Mapped[str] = mapped_column()
    config_key: Mapped[str] = mapped_column()
    active: Mapped[bool] = mapped_column(default=True)