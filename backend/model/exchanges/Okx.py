from typing import Optional

from model.exchanges.BaseExchange import BaseExchange


class Okx(BaseExchange):
    name: Optional[str] = "Okx"
    ccxt_id: Optional[str] = "okx"
    config_key: Optional[str] = "okx"

    async def load_trading_pairs(self):
        self.exchange.hostname = "my.okx.com"

        await self.load_trading_pairs_base(contract_address=["info", "ctAddr"])