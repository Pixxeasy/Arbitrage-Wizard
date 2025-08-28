import asyncio
import json
import sys
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from app.api.routers.arbitrage import router as arbitrage_router
from app.api.routers.auth import router as auth_router
from app.api.routers.exchange import router as exchange_router
from app.api.routers.health import router as health_router
from app.database.db_connector import connect
from app.services.db_init_service import init_user_data

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load global config
    with open('./config/app.json', 'r', encoding="utf-8") as file:
        config = json.load(file)

    session = connect(db_type=config["db_type"], db_name=config["db_name"])
    init_user_data("app\\database", session())
    yield
    session().close()

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
