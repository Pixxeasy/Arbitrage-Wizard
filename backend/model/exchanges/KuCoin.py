import asyncio
from typing import Optional

from ccxt.base.errors import ExchangeError, InvalidNonce, RequestTimeout

from .BaseExchange import BaseExchange
from ..Orders import OrderBook


class KuCoin(BaseExchange):

    name: Optional[str] = "KuCoin"
    ccxt_id: Optional[str] = "kucoin"
    config_key: Optional[str] = "kuc"

    async def load_trading_pairs(self):
        self.exchange.timeout = 30000

        await self.load_trading_pairs_base(info_active={"key": "enableTrading", "value": True}, contract_address=["info", "contractAddress"])

    async def get_orders(self, symbol) -> OrderBook:
        try:
            orderbook = await self.exchange.fetch_order_book(symbol)
        except ExchangeError:
            await asyncio.sleep(1)
            return await self.get_orders(symbol)
        except InvalidNonce:
            await self.exchange.load_time_difference()
            return await self.get_orders(symbol)
        except RequestTimeout:
            await self.exchange.load_time_difference()
            await asyncio.sleep(1)
            return await self.get_orders(symbol)

        return self.create_order_book(symbol, orderbook)