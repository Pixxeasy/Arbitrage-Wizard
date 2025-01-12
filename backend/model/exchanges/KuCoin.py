import asyncio
from typing import Optional

from ccxt.base.errors import ExchangeError, InvalidNonce

from model.TradingPair import TradingPair, Chain
from .BaseExchange import BaseExchange
from ..Orders import OrderBook, Order


class KuCoin(BaseExchange):

    name: Optional[str] = "KuCoin"
    ccxt_id: Optional[str] = "kucoin"
    config_key: Optional[str] = "kuc"

    async def load_trading_pairs(self):
        self.set_api()
        self.exchange.adjustForTimeDifference = True

        symbols = await self.exchange.fetch_markets()
        currencies = await self.exchange.fetch_currencies()
    
        for symbol in symbols:
            if symbol["type"] != "spot":
                continue

            if symbol["quote"] == "USDT" and symbol["info"]["enableTrading"]:
                if symbol["base"] not in currencies.keys():
                    continue      
                cur_chains = currencies[symbol["base"]]["networks"]
                pair = TradingPair(symbol=symbol["symbol"], exchange=self.config_key, fee=float(symbol["taker"]))

                for key, c in cur_chains.items():

                    if c["active"]:
                        chain = Chain(name=key, fee=float(symbol["taker"]), withdraw=c["withdraw"], deposit=c["deposit"],
                                      contract_address=c["info"]["contractAddress"], min_amount=float(c["limits"]["withdraw"]["min"]))

                        pair.add_chain(chain)

                self.trading_pairs[pair.symbol] = pair

    async def get_orders(self, symbol) -> OrderBook:
        try:
            orderbook = await self.exchange.fetch_order_book(symbol)
        except ExchangeError as e:
            print(e)
            await asyncio.sleep(1)
            return await self.get_orders(symbol)
        except InvalidNonce as In:
            print(In)
            await self.exchange.load_time_difference()
            return await self.get_orders(symbol)

        maker_fee = self.trading_pairs[symbol].fee

        book = OrderBook(buy_fee=maker_fee, sell_fee=maker_fee)

        for ask in orderbook["asks"]:
            o = Order(price=float(ask[0]), quantity=float(ask[1]))
            book.buy_orders.append(o)

        for bid in orderbook["bids"]:
            o = Order(price=float(bid[0]), quantity=float(bid[1]))
            book.sell_orders.append(o)

        return book