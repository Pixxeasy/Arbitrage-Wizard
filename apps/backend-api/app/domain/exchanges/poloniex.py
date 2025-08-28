from typing import Optional

from app.domain.exchanges.base_exchange import BaseExchange


class Poloniex(BaseExchange):
    name: Optional[str] = "Poloniex"
    ccxt_id: Optional[str] = "poloniex"
    config_key: Optional[str] = "pol"

    async def load_trading_pairs(self):
        await self.load_trading_pairs_base()
