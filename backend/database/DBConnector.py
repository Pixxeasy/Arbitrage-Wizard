import os

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

def connect(config):
    global SessionLocal

    connection_string = f"sqlite:///./conf/{config['db_name']}"
    type = config["db_type"]
    if type == "sqlite":
        connection_string = f"sqlite:///./conf/{config['db_name']}"


    elif type == "mysql":
        DB_USER = os.getenv("DB_USER")
        DB_PASSWORD = os.getenv("DB_PASSWORD")

        DB_HOST = os.getenv("DB_HOST")
        DB_PORT = os.getenv("DB_PORT", "3306")
        DB_NAME = os.getenv("DB_NAME", "arbitrage-wizard")

        connection_string = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    engine = create_engine(connection_string, echo = False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(engine)

    return SessionLocal