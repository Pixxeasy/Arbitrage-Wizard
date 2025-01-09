from sqlalchemy import Column, String
from sqlalchemy.orm import validates
from passlib.hash import pbkdf2_sha256


from database.model.BaseModel import Base
import uuid

class UserDBO(Base):
    __tablename__ = 'users'

    name: str = Column('name', String)
    salt: str| None = Column('salt', String)
    pw_hash: str| None = Column('pw_hash', String)
    guid: str  = Column('guid', String, primary_key=True)

    @validates("name")
    def generate_uuid(self, key, value):
        if not value:
            raise ValueError("username cannot be empty.")

        if not self.guid:
            self.guid = str(uuid.uuid4())
            self.salt = str(uuid.uuid4())
        return value

    def set_password(self, password: str):
        self.pw_hash = pbkdf2_sha256.using(salt=self.salt.encode(encoding="utf-8")).hash(password)