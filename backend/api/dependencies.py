from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends

from database.DBConnector import get_db

DBSessionDep = Annotated[Session, Depends(get_db)]