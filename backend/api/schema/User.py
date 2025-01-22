from typing import Optional

from pydantic import BaseModel

class UserConfig(BaseModel):
    max_amount: float
    exchange_key: str
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    api_passphrase: Optional[str] = None

    class Config:
        from_attributes = True