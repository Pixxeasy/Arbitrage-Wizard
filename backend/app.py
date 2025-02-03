import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from api.router.auth import router as auth_router
from api.router.arbitrage import router as arbitrage_router
from api.router.exchange import router as exchange_router
from api.router.health import router as health_router
from database.DBConnector import connect
from database.data_loader import init_user_data
from scanner.ScanRunner import ScanRunner
from scanner import util
import threading
import asyncio
import sys

from starlette.middleware.cors import CORSMiddleware

if sys.platform == 'win32':
	asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load global config
    with open('./conf/config.json','r', encoding="utf-8") as file:
        config = json.load(file)

    util.DEBUG = config['debug']
    session = connect(config)


    runner = ScanRunner(config["search_interval"], session())
    init_user_data("initData", session())
    thread = threading.Thread(target=asyncio.run, args=(runner.start(config["exchanges"]),))
    thread.start()
    yield
    session().close()
    await runner.stop()

app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(arbitrage_router)
app.include_router(exchange_router)
app.include_router(health_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",
                   "https://app.arbitrage-wizard.de"],  # Allow this origin (your local frontend)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.exception_handler(RequestValidationError)
async def validate_exception_handler():
    return JSONResponse(
        status_code=422,
        content={"message": "Validation error"},
    )