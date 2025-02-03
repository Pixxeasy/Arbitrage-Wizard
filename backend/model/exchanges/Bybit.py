from typing import Optional

from model.exchanges.BaseExchange import BaseExchange


class Bybit(BaseExchange):
    name: Optional[str] = "Bybit"
    ccxt_id: Optional[str] = "bybit"
    config_key: Optional[str] = "byb"

    async def load_trading_pairs(self):
        await self.exchange.load_time_difference()

        await self.load_trading_pairs_base(contract_address=["info", "contractAddress"])