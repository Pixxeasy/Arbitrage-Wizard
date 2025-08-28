import uuid
from typing import Optional, List

from passlib.hash import pbkdf2_sha256
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, validates, relationship

from app.database.models.base import BaseDBO
from app.database.models.user_config import UserConfigDBO


class UserDBO(BaseDBO):
    __tablename__ = 'users'

    name: Mapped[str] = mapped_column(String(50))
    pw_hash: Mapped[Optional[str]] = mapped_column(String(300))
    salt: Mapped[Optional[str]] = mapped_column(String(100))
    configs: Mapped[List["UserConfigDBO"]] = relationship()

    @validates("name")
    def generate_salt(self, key, value):
        self.salt = str(uuid.uuid4())
        return value

    def set_password(self, password: str):
        self.pw_hash = pbkdf2_sha256.using(salt=self.salt.encode(encoding="utf-8")).hash(password)
