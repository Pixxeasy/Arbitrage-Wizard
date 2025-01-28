from typing import Dict, Optional

from pydantic import BaseModel, Field, field_validator

ALLOWED_CHAINS = ["BTC","ERC20","XRP","ETH","LTC","DOGE","XLM","TRC20","BEP20","XMR","ADA","XTZ","SOL","BEP2","DOT",
                  "AVAX","RUNE","NEAR","THETA","STX","ARBITRUM","MATIC","FTM"]

class Chain(BaseModel):

    name: str
    fee: float = Field(ge=0)
    withdraw: bool
    deposit: bool
    contract_address: Optional[str] = None
    min_amount: float = Field(ge=0)

    @field_validator('contract_address', mode="before")
    @classmethod
    def lower_contract_address(cls, v):
        if v:
            return v.lower()
        else:
            return v

    @field_validator('name', mode="before")
    @classmethod
    def convert_name(cls, v):
        if v:
            return cls._convert_chain_name(v)
        raise ValueError("name cannot be none")

    @classmethod
    def _convert_chain_name(cls,name: str) -> str:
        
        return name

    def is_allowed_chain(self) -> bool:
        return self.name in ALLOWED_CHAINS

    def has_contract_address(self):
        return self.contract_address is not None

class TradingPair(BaseModel):

    symbol: str
    sell_price: Optional[float] = Field(None,gt=0)
    buy_price: Optional[float] = Field(None,gt=0)
    fee: float = Field(ge=0)
    exchange: str
    chains: Dict[str, Chain] = Field(default={})

    def add_chain(self, chain:Chain):
        self.chains[chain.name] = chain
        
    def get_chain(self, name:str):
        if name in self.chains.keys():
            return self.chains[name]
        
        return None