from typing import List, Dict, Any
import pandas as pd
from api.dependencies import DBSessionDep

from pydantic import BaseModel, Field

from database.model.ArbitrageOpportunity import ArbitrageGroupDBO, ArbitrageOpportunityDBO

class ArbitrageOpportunity(BaseModel):

    min_usdt_start: float = Field(None,gt=0)
    min_usdt_end: float = Field(None,gt=0)
    max_usdt_start: float = Field(None,gt=0)
    max_usdt_end: float = Field(None,gt=0)
    min_profit: float = Field(None,gt=0)
    max_profit: float = Field(None,gt=0)
    buy_price: float = Field(None,gt=0)
    sell_price: float = Field(None,gt=0)

    def to_DBO(self):
        dbo = ArbitrageOpportunityDBO(**self.model_dump())
        return dbo

    class Config:
        from_attributes = True

class ArbitrageGroup(BaseModel):

    buy_exchange_name: str
    sell_exchange_name: str
    buy_exchange_id: str
    sell_exchange_id: str
    trading_pair: str
    chain: str
    opportunities: List[ArbitrageOpportunity] = Field(default=[])

    def add_opportunity(self, opportunity: ArbitrageOpportunity):
        self.opportunities.append(opportunity)

    def set_opportunities(self, opportunities: List[ArbitrageOpportunity]):
        self.opportunities = opportunities

    def to_dict(self) -> Dict[str,Any]:
        df = pd.DataFrame([o.model_dump() for o in self.opportunities])

        return {
            "tradingPair": self.trading_pair,
            "buyExchange": self.buy_exchange_name,
            "buyPrice": df["buy_price"].mean(),
            "minStartAmount": df["min_usdt_start"].mean(),
            "maxStartAmount": df["max_usdt_start"].mean(),
            "minEndAmount": df["min_usdt_end"].mean(),
            "maxEndAmount": df["max_usdt_end"].mean(),
            "chain": self.chain,
            "sellExchange": self.sell_exchange_name,
            "sellPrice": df["sell_price"].mean(),
            "minProfit": df["min_profit"].mean(),
            "maxProfit": df["max_profit"].mean(),
            "opportunities": len(self.opportunities),
        }

    def to_DBO(self):
        dbo = ArbitrageGroupDBO(buy_exchange_id=self.buy_exchange_id, sell_exchange_id=self.sell_exchange_id,
                                trading_pair=self.trading_pair, chain=self.chain)
        for op in self.opportunities:
            dbo.opportunities.append(op.to_DBO())

        return dbo

class Possibility(BaseModel):

    min_usdt_amount:float = Field(gt=0)
    max_usdt_amount:float = Field(ge=0)
    rate:float = Field(gt=0)
    min_coin_amount:float = Field(gt=0)
    max_coin_amount:float = Field(ge=0)