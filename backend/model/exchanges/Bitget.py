from typing import Optional
from .BaseExchange import BaseExchange


class Bitget(BaseExchange):

    name: Optional[str] = "Bitget"
    ccxt_id: Optional[str] = "bitget"
    config_key: Optional[str] = "btg"

    async def load_trading_pairs(self):

       await self.load_trading_pairs_base(info_active={"key": "status", "value": "online"},contract_address=["info", "contractAddress"])