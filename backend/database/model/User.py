from sqlalchemy.orm import Mapped, mapped_column, validates
from typing import Optional
from passlib.hash import pbkdf2_sha256


from database.model.BaseModel import BaseDBO
import uuid

class UserDBO(BaseDBO):
    __tablename__ = 'users'

    name: Mapped[str] = mapped_column()
    pw_hash: Mapped[Optional[str]] = mapped_column()
    salt: Mapped[Optional[str]] = mapped_column()

    @validates("name")
    def generate_salt(self, key,value):
        self.salt = str(uuid.uuid4())
        return value

    def set_password(self, password: str):
        self.pw_hash = pbkdf2_sha256.using(salt=self.salt.encode(encoding="utf-8")).hash(password)