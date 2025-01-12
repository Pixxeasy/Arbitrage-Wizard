import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from api.router.auth import router as auth_router
from database.DBConnector import connect
from database.data_loader import init_user_data
from scanner.ScanRunner import ScanRunner


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load global config
    with open('./conf/config.json','r', encoding="utf-8") as file:
        config = json.load(file)

    session = connect(f"./conf/{config['db_name']}")
    with session() as db:
        runner = ScanRunner(config["search_interval"], db)
        init_user_data("initData", db)
        await runner.start(config["exchanges"])
    yield
    await runner.stop()

app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)

@app.exception_handler(RequestValidationError)
async def validate_exception_handler():
    return JSONResponse(
        status_code=422,
        content={"message": "Validation error"},
    )