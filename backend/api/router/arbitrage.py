from fastapi import APIRouter
from typing import List

from api.dependencies import DBSessionDep, UserDep
from api.schema.Arbitrage import ArbitrageGroupResponse
from api.handler.ArbitrageHandler import get_current_arbitrage_by_user_config

router = APIRouter(
    prefix="/api/arbitrage",
    tags=["arbitrage"],
    responses={404: {"description": "Not found"}},
)

@router.get("/current")
async def get_current_arbitrages(user: UserDep,db: DBSessionDep):
    user_config = {"max_amount": 100}

    dbos,ts = get_current_arbitrage_by_user_config(user_config,db)

    return {"last_update": ts, "arbitrages": dbos}
