from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import DBSessionDep
from app.schemas.login_credentials import Token
from app.services.user_service import handle_login, create_access_token

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/login",
    response_model=Token
)
async def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: DBSessionDep
) -> Token:
    user = handle_login(form_data.username, form_data.password, db)
    if not form_data:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    if not form_data.username or not form_data.password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="")
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"}, )

    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": user.name}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
