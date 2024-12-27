from contextlib import asynccontextmanager

from fastapi import FastAPI
import json
import asyncio
from scanner.ScanRunner import ScanRunner
from database.DBConnector import DBConnector

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load global config
    with open('./conf/config.json','r', encoding="utf-8") as file:
        config = json.load(file)
    runner = ScanRunner(config["search_interval"])
    con = DBConnector(f"./conf/{config['db_name']}")
    con.connect()
    await runner.start(con, config["exchanges"])
    yield
    await runner.stop()


app = FastAPI(lifespan=lifespan)