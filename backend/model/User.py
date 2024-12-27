from sqlalchemy import Column, Integer, String

from .BaseModel import Base

class User(Base):
    __tablename__ = 'users'

    guid = Column(String, primary_key=True)
    name = Column(String)
    password = Column(String)
    salt = Column(String)