from fastapi import APIRouter
from typing import List

from api.dependencies import DBSessionDep, UserDep
from api.handler import ExchangeHandler
from api.schema.Arbitrage import ArbitrageGroupResponse
from api.schema.Exchange import SimpleExchange
from api.schema.User import UserConfig

router = APIRouter(
    prefix="/api/exchange",
    tags=["arbitrage"],
    responses={404: {"description": "Not found"}},
)

@router.get("/available")
async def get_available_exchanges(user: UserDep,db: DBSessionDep) -> List[SimpleExchange]:

    exchanges = ExchangeHandler.get_available_exchanges(db)

    return exchanges

@router.get("/userConfig")
async def get_user_configs(user: UserDep,db: DBSessionDep) -> List[UserConfig]:

    configs = ExchangeHandler.get_user_configs(db, user)

    return configs

@router.post("/userConfig/add")
async def add_user_configs(configs: List[UserConfig],user: UserDep,db: DBSessionDep) -> List[UserConfig]:

    configs = ExchangeHandler.add_user_configs(db, configs, user)

    return configs

@router.post("/userConfig/edit")
async def edit_user_configs(configs: list[UserConfig],user: UserDep,db: DBSessionDep) -> List[UserConfig]:

    configs = ExchangeHandler.edit_user_configs(db, configs, user)

    return configs