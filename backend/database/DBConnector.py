from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from database.model.BaseModel import Base

SessionLocal = None
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def connect(path):
    global SessionLocal
    engine = create_engine(f"sqlite:///{path}", echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(engine)

    return SessionLocal