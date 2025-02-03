import datetime

from fastapi import APIRouter, HTTPException

import model.ExchangeInfo as ExchangeInfo

router = APIRouter(
    prefix="/api",
    tags=["health"],
    responses={404: {"description": "Not found"}},
)

@router.get("/health")
async def get_health():

    return {"health": "OK"}

@router.get("/health/scanner")
async def get_scanner_health():
    last_time = ExchangeInfo.get_last_total_time(1)
    if not last_time:
        return {"scanner": "OK"}

    if int(datetime.datetime.now().timestamp()) - last_time > 90:
        raise HTTPException(status_code=500, detail="Scanner not running")

    return {"health": "OK"}


