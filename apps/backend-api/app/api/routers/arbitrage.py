from fastapi import APIRouter

from app.api.dependencies import DBSessionDep, UserDep
from app.services.arbitrage_service import get_current_arbitrage_by_user_config, get_historic_arbitrages

router = APIRouter(
    prefix="/api/arbitrage",
    tags=["arbitrage"],
    responses={404: {"description": "Not found"}},
)


@router.get("/current")
async def get_current_arbitrages(user: UserDep, db: DBSessionDep):
    dbos, ts = get_current_arbitrage_by_user_config(user, db)

    return {"last_update": ts, "arbitrages": dbos}


@router.get("/history")
async def get_history_arbitrages(user: UserDep, db: DBSessionDep):
    dbos = get_historic_arbitrages(db)

    return dbos
