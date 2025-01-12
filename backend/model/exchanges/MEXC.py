from typing import Optional

from model.TradingPair import TradingPair, Chain
from .BaseExchange import BaseExchange


class MEXC(BaseExchange):

    name: Optional[str] = "MEXC"
    ccxt_id: Optional[str] = "mexc"
    config_key: Optional[str] = "mxc"

    async def load_trading_pairs(self):
        self.set_api()
        self.exchange.enableRateLimit = True
        self.exchange.rateLimit = 20

        symbols = await self.exchange.fetch_markets()
        
        currencies = await self.exchange.fetch_currencies()

        for symbol in symbols:
            if symbol["type"] != "spot":
                continue

            if symbol["quote"] == "USDT" and symbol["info"]["status"]=="1":
                if symbol["base"] not in currencies.keys():
                    continue      
                cur_chains = currencies[symbol["base"]]["networks"]
                pair= TradingPair(symbol=symbol["symbol"], exchange=self.config_key, fee=float(symbol["taker"]))
                       
                for key, c in cur_chains.items():

                    if c["withdraw"]:
                        chain = Chain(name=key, fee=float(c["fee"]), withdraw=c["withdraw"], deposit=c["deposit"],
                                      contract_address=c["info"]["contract"], min_amount=float(c["limits"]["withdraw"]["min"]) )

                        pair.add_chain(chain)

                self.trading_pairs[pair.symbol] = pair