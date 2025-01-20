from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from api.handler.UserHandler import get_user_by_token
from database.DBConnector import get_db
from database.model.User import UserDBO

DBSessionDep = Annotated[Session, Depends(get_db)]
UserDep = Annotated[UserDBO, Depends(get_user_by_token)]