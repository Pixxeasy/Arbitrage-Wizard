import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from database.model.BaseModel import Base
from google.cloud.sql.connector import Connector
import pymysql
import sys
import asyncio

SessionLocal = None
connector = Connector()
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def connect(config):
    global SessionLocal

    type = config["db_type"]
    if type == "sqlite":
        connection_string = f"sqlite:///./conf/{config['db_name']}"
        engine = create_engine(connection_string, echo=False)

    elif type == "mysql":
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