from typing import Annotated

from model.User import  User
from sqlalchemy.orm.session import Session
from passlib.hash import pbkdf2_sha256
from datetime import timedelta, datetime, timezone
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

import jwt

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def handleLogin(username, password, session: Session):
    user = session.query(User).filter(User.name == username).first()
    if not user:
        return user
    if pbkdf2_sha256.using(salt=user.salt.encode(encoding="utf-8")).verify(password, user.password):
        return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_user(token: Annotated[str, Depends(oauth2_scheme)], session: Session):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        expire: str = payload.get("exp")
        if username is None:
            raise credentials_exception

        if datetime.now() > expire:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception
    user = session.query(User).filter(User.name == username).first()
    if user is None:
        raise credentials_exception
    return user


