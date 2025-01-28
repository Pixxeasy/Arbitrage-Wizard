from typing import Optional

from .BaseExchange import BaseExchange
from ccxt.base.errors import ExchangeError, RequestTimeout
import asyncio


class XT(BaseExchange):

    name: Optional[str] = "XT"
    ccxt_id: Optional[str] = "xt"
    config_key: Optional[str] = "xt"

    async def load_trading_pairs(self):

        await self.load_trading_pairs_base(info_active={"key": "state", "value": "ONLINE"}, contract_address=["info", "contract"], fee_rate="takerFeeRate")
    
    async def load_prices(self):

        try:
            prices = await self.exchange.fetch_bids_asks()
        except ExchangeError as e:
            print(e)
            await asyncio.sleep(1)
            return self.load_prices()
        except RequestTimeout:
            return await self.load_prices()

        self.add_prices(prices)
        return