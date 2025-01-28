from typing import Optional
from model.exchanges.BaseExchange import BaseExchange


class BingX(BaseExchange):
    name: Optional[str] = "BingX"
    ccxt_id: Optional[str] = "bingx"
    config_key: Optional[str] = "bnx"

    async def load_trading_pairs(self):

        await self.load_trading_pairs_base(contract_address=["info", "contractAddress"])