from contextlib import asynccontextmanager
from urllib.request import Request

from fastapi import FastAPI
import json
import asyncio
from scanner.ScanRunner import ScanRunner
from database.DBConnector import DBConnector

@asynccontextmanager
async def lifespan(app: FastAPI):
    global session
    # Load global config
    with open('./conf/config.json','r', encoding="utf-8") as file:
        config = json.load(file)
    runner = ScanRunner(config["search_interval"])
    con = DBConnector(f"./conf/{config['db_name']}")
    session = con.connect()
    await runner.start(con, config["exchanges"])
    yield
    await runner.stop()


app = FastAPI(lifespan=lifespan)

@app.post("/login")
async def login(request: Request):
    return {"message": "Hello World"}