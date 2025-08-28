from typing import List, Optional

from pydantic import BaseModel, Field

from app.domain.arbitrage import ArbitrageOpportunity


class ArbitrageGroupResponse(BaseModel):
    trading_pair: str
    chain_name: str = Field(validation_alias="chain")
    buy_exchange_name: Optional[str] = Field(None)
    sell_exchange_name: Optional[str] = Field(None)
    opportunities: List[ArbitrageOpportunity]

    class Config:
        from_attributes = True


class HistoricArbitrage(BaseModel):
    trading_pair: str
    series_start: int
    series_end: int
    num_runs: int
    sell_exchange_key: str
    buy_exchange_key: str
    buy_exchange_name: Optional[str] = None
    sell_exchange_name: Optional[str] = None
