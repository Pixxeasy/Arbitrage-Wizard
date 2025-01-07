from contextlib import asynccontextmanager
from typing import Annotated
from urllib.request import Request
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from model.api.LoginCredentials import LoginCredentials
from datetime import datetime, timedelta, timezone
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from fastapi import FastAPI
import json
import asyncio
from scanner.ScanRunner import ScanRunner
from database.DBConnector import DBConnector
from database.UserHandler import handleLogin, create_access_token
from model.api.LoginCredentials import Token

@asynccontextmanager
async def lifespan(app: FastAPI):
    global session
    # Load global config
    with open('./conf/config.json','r', encoding="utf-8") as file:
        config = json.load(file)
    runner = ScanRunner(config["search_interval"])
    con = DBConnector(f"./conf/{config['db_name']}")
    session = con.connect()
    #await runner.start(con, config["exchanges"])
    yield
    await runner.stop()


app = FastAPI(lifespan=lifespan)

@app.exception_handler(RequestValidationError)
async def validate_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"message": "Validation error"},
    )

@app.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = handleLogin(form_data.username, form_data.password, session)
    if not form_data:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    if not form_data.username or not form_data.password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="")
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"},)

    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": user.name}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
