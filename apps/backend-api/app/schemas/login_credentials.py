from pydantic import BaseModel


class LoginCredentials(BaseModel):
    username: str
    password: str


class LoginResult(BaseModel):
    token: str
    expires: int
    success: bool

    def __init__(self, token: str, expires: int, success: bool) -> None:
        self.token = token
        self.expires = expires
        self.success = success


class Token(BaseModel):
    access_token: str
    token_type: str
