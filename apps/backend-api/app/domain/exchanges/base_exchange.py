import asyncio
import os
import uuid
from typing import Dict, Any, Self, Optional

import ccxt.async_support as ccxt
from ccxt import RateLimitExceeded
from ccxt.base.errors import ExchangeError, ExchangeNotAvailable, RequestTimeout, InvalidNonce
from pydantic import BaseModel, Field, model_validator

from app.domain.orders import Order, OrderBook
from app.domain.trading_pair import TradingPair, Chain
from scanner import util

namespace = uuid.UUID("1b4b0697-54a1-4e3b-b3c4-ca83f29e2499")


class BaseExchange(BaseModel):
    name: str = Field()
    guid: Optional[str] = None
    config_key: str
    ccxt_id: str
    trading_pairs: Dict[str, TradingPair] = Field(default=dict)
    apiKey: str | None = None
    apiSecret: str | None = None
    passphrase: str | None = None
    exchange: Any = None

    @model_validator(mode='after')
    def init(self) -> Self:
        name = self.name.upper()
        self.apiKey = os.getenv(f"{name}_API_KEY")
        self.apiSecret = os.getenv(f"{name}_API_SECRET")
        self.passphrase = os.getenv(f"{name}_API_PASSPHRASE")

        self.exchange = getattr(ccxt, self.ccxt_id)()
        self.set_api()
        return self

    def set_api(self):
        if self.apiKey:
            self.exchange.apiKey = self.apiKey

        if self.apiSecret:
            self.exchange.secret = self.apiSecret

        if self.passphrase:
            self.exchange.password = self.passphrase

    def add_prices(self, prices):
        for symbol, ticker in prices.items():

            if symbol[-4:].upper() == "USDT":

                if symbol in list(self.trading_pairs.keys()):
                    if ticker["ask"]:
                        self.trading_pairs[symbol].buy_price = float(ticker["ask"])
                    if ticker["bid"]:
                        self.trading_pairs[symbol].sell_price = float(ticker["bid"])

        return

    async def load_prices(self):
        if not self.exchange.has['fetchTickers']:
            print("Exchange " + self.name + " does not support ticker")
            return

        try:
            prices = await self.exchange.fetch_tickers()
        except RequestTimeout:
            await asyncio.sleep(1)
            return await self.load_prices()
        except InvalidNonce:
            await self.exchange.load_time_difference()
            return await self.load_prices()

        self.add_prices(prices)
        return

    def create_order_book(self, symbol, data):
        maker_fee = self.trading_pairs[symbol].fee
        book = OrderBook(buy_fee=maker_fee, sell_fee=maker_fee)

        for ask in data["asks"]:
            if (ask[0] <= 0) or (ask[1] <= 0):
                continue
            o = Order(price=float(ask[0]), quantity=float(ask[1]))
            book.buy_orders.append(o)

        for bid in data["bids"]:
            if (bid[0] <= 0) or (bid[1] <= 0):
                continue
            o = Order(price=float(bid[0]), quantity=float(bid[1]))
            book.sell_orders.append(o)

        return book

    async def get_orders(self, symbol) -> OrderBook:
        try:
            orderbook = await self.exchange.fetch_order_book(symbol)
        except RequestTimeout:
            if util.DEBUG:
                print(f"{self.name}: Request timed out")
            await asyncio.sleep(1)
            return await self.get_orders(symbol)
        except ExchangeError:
            print(f"{self.name}: ExchangeError")
            return None
        except ExchangeNotAvailable:
            print(f"{self.name} Exchange not available")
            return None
        except RateLimitExceeded:
            print(f"{self.name} Exchange rate limit exceeded")
            await asyncio.sleep(5)
            return await self.get_orders(symbol)

        return self.create_order_book(symbol, orderbook)

    async def load_trading_pairs_base(self, info_active=None, contract_address=[], currencies=None, fee_rate=None):

        # Load all symbols
        try:
            symbols = await self.exchange.fetch_markets()
        except RequestTimeout:
            await asyncio.sleep(1)
            symbols = await self.exchange.fetch_markets()

        # Load all currencies
        if not currencies:
            try:
                currencies = await self.exchange.fetch_currencies()
            except RequestTimeout:
                await asyncio.sleep(1)
                currencies = await self.exchange.fetch_currencies()

        for symbol in symbols:
            if symbol["type"] != "spot":
                continue

            if symbol["quote"] != "USDT":
                continue

            if info_active:
                if symbol["info"][info_active["key"]] != info_active["value"]:
                    continue
            else:
                if not symbol["active"]:
                    continue

            if symbol["base"] not in currencies.keys():
                continue

            if "networks" in currencies[symbol["base"]].keys():
                cur_chains = currencies[symbol["base"]]["networks"]
            else:
                cur_chains = currencies[symbol["base"]]

            if "taker" in symbol.keys() or fee_rate:
                taker_rate = symbol["info"][fee_rate] if fee_rate else symbol["taker"]
            else:
                taker_rate = self.exchange.fees["trading"]["taker"]

            pair = TradingPair(symbol=symbol["symbol"], exchange=self.config_key, fee=float(taker_rate))

            for key, c in cur_chains.items():
                if c["deposit"] or c["withdraw"]:
                    fee = 0 if c["fee"] is None else c["fee"]

                    if "min_amount" in c.keys():
                        min_amount = c["min_amount"]
                    else:
                        min_amount = 0 if c["limits"]["withdraw"]["min"] is None else float(
                            c["limits"]["withdraw"]["min"])

                    if len(contract_address) == 2:
                        contract_address_value = None if len(contract_address) == 0 else c[contract_address[0]][
                            contract_address[1]]
                    else:
                        contract_address_value = None if len(contract_address) == 0 else c[contract_address[0]]

                    chain = Chain(name=key, fee=float(fee), withdraw=c["withdraw"],
                                  deposit=c["deposit"], contract_address=contract_address_value,
                                  min_amount=min_amount)
                    pair.add_chain(chain)

            self.trading_pairs[pair.symbol] = pair
