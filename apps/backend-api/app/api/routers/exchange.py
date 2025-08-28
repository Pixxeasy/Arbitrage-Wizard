from typing import List

from fastapi import APIRouter

from app.api.dependencies import DBSessionDep, UserDep
from app.schemas.exchange import SimpleExchange
from app.schemas.user import UserConfig
from app.services import exchange_service

router = APIRouter(
    prefix="/api/exchange",
    tags=["arbitrage"],
    responses={404: {"description": "Not found"}},
)


@router.get("/available")
async def get_available_exchanges(user: UserDep, db: DBSessionDep) -> List[SimpleExchange]:
    exchanges = exchange_service.get_available_exchanges(db)

    return exchanges


@router.get("/userConfig")
async def get_user_configs(user: UserDep, db: DBSessionDep) -> List[UserConfig]:
    configs = exchange_service.get_user_configs(db, user)

    return configs


@router.post("/userConfig/add")
async def add_user_configs(configs: List[UserConfig], user: UserDep, db: DBSessionDep) -> List[UserConfig]:
    configs = exchange_service.add_user_configs(db, configs, user)

    return configs


@router.post("/userConfig/edit")
async def edit_user_configs(configs: list[UserConfig], user: UserDep, db: DBSessionDep) -> List[UserConfig]:
    configs = exchange_service.edit_user_configs(db, configs, user)

    return configs
