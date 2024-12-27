
from sqlalchemy import Column, Integer, String

from model.BaseModel import Base
import uuid
import os

namespace = uuid.UUID("1b4b0697-54a1-4e3b-b3c4-ca83f29e2499")

class BaseExchange(Base):
    __tablename__ = 'exchanges'

    guid = Column(String, primary_key=True)
    name = Column(String)
    configKey = Column(String)

    def __init__(self, name: str, configKey):
        self.name = name
        self.configKey = configKey
        self.guid = str(uuid.uuid5(namespace, f"exchange:{configKey}"))
        self.tradingPairs = []
        self.apiKey = os.getenv(f"{name.upper()}_API_KEY")
        self.apiSecret = os.getenv(f"{name.upper()}_API_SECRET")
        self.passphrase = os.getenv(f"{name.upper()}_API_PASSPHRASE")