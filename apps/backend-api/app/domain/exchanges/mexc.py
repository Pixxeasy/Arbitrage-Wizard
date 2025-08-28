import asyncio
import json
from asyncio import Semaphore
from datetime import datetime
from typing import Optional, Any

from ccxt import RequestTimeout, ExchangeError

from .base_exchange import BaseExchange
from ..orders import OrderBook


class MEXC(BaseExchange):
    name: Optional[str] = "MEXC"
    ccxt_id: Optional[str] = "mexc"
    config_key: Optional[str] = "mxc"

    sem: Optional[Any] = Semaphore(3)
    last_price_fetch: Optional[float] = None

    async def load_trading_pairs(self):
        await self.load_trading_pairs_base(info_active={"key": "status", "value": "1"},
                                           contract_address=["info", "contract"])

    async def load_prices(self):
        if self.last_price_fetch and ((int(datetime.now().timestamp()) - self.last_price_fetch) < 50):
            print("price fetch time exceeded")
            return

        if not self.exchange.has['fetchTickers']:
            print("Exchange " + self.name + " does not support ticker")
            return

        try:
            prices = await self.exchange.fetch_tickers()
            self.last_price_fetch = int(datetime.now().timestamp())
        except RequestTimeout:
            return await self.load_prices()

        self.add_prices(prices)
        return

    async def get_orders(self, symbol) -> OrderBook:
        try:
            async with self.sem:
                orderbook = await self.exchange.fetch_order_book(symbol)

        except ExchangeError:
            resp_http = self.exchange.last_http_response

            resp_json = json.loads(resp_http)
            if int(resp_json["code"]) == 429:
                print(f"{self.name} Too many requests")
                headers = self.exchange.last_response_headers
                if "Retry-After" in headers.keys():
                    seconds = headers["Retry-After"]
                    await asyncio.sleep(int(seconds))
                await asyncio.sleep(5)

            return await self.get_orders(symbol)
        except RequestTimeout:
            await asyncio.sleep(1)
            try:
                await self.exchange.load_time_difference()
            except RequestTimeout:
                return await self.get_orders(symbol)

            return await self.get_orders(symbol)

        return self.create_order_book(symbol, orderbook)
