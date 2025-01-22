from typing import Optional

from database.model.BaseModel import BaseDBO
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey


class UserConfigDBO(BaseDBO):
    __tablename__ = 'user_configs'

    max_amount: Mapped[float]
    exchange_key: Mapped[str] = mapped_column(ForeignKey('exchanges.config_key'))
    user_id: Mapped[str] = mapped_column(ForeignKey('users.guid'))
    api_key: Mapped[Optional[str]]
    api_secret: Mapped[Optional[str]]
    api_passphrase: Mapped[Optional[str]]