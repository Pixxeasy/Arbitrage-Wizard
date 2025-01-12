import asyncio
import os
import uuid
from typing import Dict, Any, Self, Optional

import ccxt.async_support as ccxt
from ccxt.base.errors import ExchangeError, ExchangeNotAvailable
from pydantic import BaseModel, Field, model_validator

from model.Orders import Order, OrderBook
from model.TradingPair import TradingPair

namespace = uuid.UUID("1b4b0697-54a1-4e3b-b3c4-ca83f29e2499")

class BaseExchange(BaseModel):

    name: str = Field()
    guid: Optional[str] = None
    config_key: str
    ccxt_id: str
    trading_pairs: Dict[str, TradingPair] = Field(default={})
    apiKey: str | None = None
    apiSecret: str| None = None
    passphrase: str| None = None
    exchange: Any = None

    @model_validator(mode='after')
    def init(self) -> Self:
        name = self.name.upper()
        self.apiKey = os.getenv(f"{name}_API_KEY")
        self.apiSecret = os.getenv(f"{name}_API_SECRET")
        self.passphrase = os.getenv(f"{name}_API_PASSPHRASE")

        self.exchange = getattr(ccxt, self.ccxt_id)()
        return self

    def set_api(self):
        if self.apiKey:
            self.exchange.apiKey = self.apiKey

        if self.apiSecret:
            self.exchange.secret = self.apiSecret

        if self.passphrase:
            self.exchange.password = self.passphrase

    async def load_prices(self):
        if not self.exchange.has['fetchTickers']:
            print("Exchange " + self.name + " does not support ticker")
        prices = await self.exchange.fetch_tickers()

        for symbol,ticker in prices.items():

            if symbol[-4:].upper() == "USDT":
               
                if symbol in list(self.trading_pairs.keys()):
                    if ticker["ask"]:
                        self.trading_pairs[symbol].buy_price = float(ticker["ask"])
                    if ticker["bid"]:
                        self.trading_pairs[symbol].sell_price = float(ticker["bid"])

    async def get_orders(self, symbol) -> OrderBook:
        try:
            orderbook = await self.exchange.fetch_order_book(symbol)
        except ExchangeError as e:
            print(e.args)
            await asyncio.sleep(1)
            return await self.getOrders(symbol)
        except ExchangeNotAvailable:
            return None

        maker_fee = self.trading_pairs[symbol].fee

        book = OrderBook(buy_fee=maker_fee, sell_fee=maker_fee)

        for ask in orderbook["asks"]:
            o = Order(price=float(ask[0]), quantity=float(ask[1]))
            book.buy_orders.append(o)

        for bid in orderbook["bids"]:
            o = Order(price=float(bid[0]), quantity=float(bid[1]))
            book.sell_orders.append(o)

        return book