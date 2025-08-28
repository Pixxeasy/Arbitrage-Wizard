from typing import Optional

from app.domain.exchanges.base_exchange import BaseExchange


class HTX(BaseExchange):
    name: Optional[str] = "HTX"
    ccxt_id: Optional[str] = "htx"
    config_key: Optional[str] = "htx"

    async def load_trading_pairs(self):
        await self.load_trading_pairs_base()
