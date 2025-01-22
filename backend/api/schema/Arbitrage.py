from typing import List, Optional

from pydantic import BaseModel, Field

from model.ArbitrageModel import ArbitrageOpportunity


class ArbitrageGroupResponse(BaseModel):

    trading_pair: str
    chain_name: str = Field(validation_alias="chain")
    buy_exchange_name: Optional[str] = Field(None)
    sell_exchange_name: Optional[str] = Field(None)
    opportunities: List[ArbitrageOpportunity]

    class Config:
        from_attributes = True