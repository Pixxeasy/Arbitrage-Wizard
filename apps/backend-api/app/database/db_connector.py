import os

import pymysql
from google.cloud.sql.connector import Connector
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database.models.base import Base

SessionLocal = None
connector = Connector()


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def connect(db_type="sqlite", db_name="data.sqlite", db_path="./config"):
    global SessionLocal

    if db_type == "sqlite":
        connection_string = f"sqlite:///{db_path}/{db_name}"
        engine = create_engine(connection_string, echo=False)

    elif db_type == "mysql":
        connection_string = f"mysql+pymysql://"
        engine = create_engine(connection_string, creator=getconn, echo=False)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(engine)

    return SessionLocal


def getconn() -> pymysql.connections.Connection:
    conn: pymysql.connections.Connection = connector.connect(
        os.getenv("DB_HOST"),
        "pymysql",
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        db=os.getenv("DB_NAME", "arbitrage_wizard_prod")
    )
    return conn
