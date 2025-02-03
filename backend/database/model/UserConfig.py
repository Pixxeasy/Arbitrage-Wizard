from typing import Optional

from database.model.BaseModel import BaseDBO
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, String


class UserConfigDBO(BaseDBO):
    __tablename__ = 'user_configs'

    max_amount: Mapped[float]
    exchange_key: Mapped[str] = mapped_column(String(3),ForeignKey('exchanges.config_key'), index=True)
    user_id: Mapped[str] = mapped_column(String(100),ForeignKey('users.guid'), index=True)
    api_key: Mapped[Optional[str]] = mapped_column(String(100))
    api_secret: Mapped[Optional[str]] = mapped_column(String(100))
    api_passphrase: Mapped[Optional[str]] = mapped_column(String(100))