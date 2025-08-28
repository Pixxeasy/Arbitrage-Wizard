from pydantic import BaseModel


class SimpleExchange(BaseModel):
    config_key: str
    name: str

    class Config:
        from_attributes = True
