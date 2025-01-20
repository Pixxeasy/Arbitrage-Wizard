from typing import Optional

from model.TradingPair import TradingPair, Chain
from .BaseExchange import BaseExchange
from ccxt.base.errors import ExchangeNotAvailable, ExchangeError
import asyncio


class XT(BaseExchange):

    name: Optional[str] = "XT"
    ccxt_id: Optional[str] = "xt"
    config_key: Optional[str] = "xt"

    async def load_trading_pairs(self):
        symbols = await self.exchange.fetch_markets()

        currencies = await self.exchange.fetch_currencies()
        for symbol in symbols:
            if symbol["type"] != "spot":
                continue

            if symbol["quote"] == "USDT" and symbol["info"]["state"]=="ONLINE":
                if symbol["base"] not in currencies.keys():
                    continue      
                cur_chains = currencies[symbol["base"]]["networks"]

                pair = TradingPair(symbol=symbol["symbol"], exchange=self.config_key, fee=float(symbol["info"]["takerFeeRate"]) )

                for key, c in cur_chains.items():

                    if c["withdraw"]:
                        chain = Chain(name=key, fee=float(c["fee"]), withdraw=c["withdraw"], deposit=c["deposit"],
                                      contract_address=c["info"]["contract"], min_amount=float(c["limits"]["withdraw"]["min"]))

                        pair.add_chain(chain)

                self.trading_pairs[pair.symbol] = pair
    
    async def load_prices(self):

        try:
            prices = await self.exchange.fetch_bids_asks()
        except ExchangeError as e:
            print(e)
            await asyncio.sleep(1)
            return self.load_prices()
        for symbol,ticker in prices.items():

            if symbol[-4:].upper() == "USDT":
               
                if symbol in list(self.trading_pairs.keys()):
                    if ticker["ask"]:
                        self.trading_pairs[symbol].buy_price = float(ticker["ask"])
                        
                    if ticker["bid"]:
                        self.trading_pairs[symbol].sell_price = float(ticker["bid"])