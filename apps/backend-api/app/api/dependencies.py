from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.db_connector import get_db
from app.database.models.user import UserDBO
from app.services.user_service import get_user_by_token

DBSessionDep = Annotated[Session, Depends(get_db)]
UserDep = Annotated[UserDBO, Depends(get_user_by_token)]
