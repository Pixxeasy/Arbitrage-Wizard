from datetime import timedelta, datetime, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.hash import pbkdf2_sha256
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.DBConnector import get_db

from database.model.User import UserDBO

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def handle_login(username, password, db: Session) -> UserDBO:
    user = get_user_by_name(username,db)
    #print(user.guid)
    #print(user.salt)
    if not user:
        return user
    if pbkdf2_sha256.using(salt=user.salt.encode(encoding="utf-8")).verify(password, user.pw_hash):
        return user

def get_user_by_name(username: str, db: Session) -> UserDBO:
    stmt = select(UserDBO).where(UserDBO.name == username)
    return db.execute(stmt).scalars().first()

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire.timestamp()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_user_by_token(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[Session, Depends(get_db)]) -> UserDBO:
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

        if datetime.now().timestamp() > expire:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception
    user = get_user_by_name(username, db)
    if user is None:
        raise credentials_exception
    return user