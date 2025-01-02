from .BaseExchange import BaseExchange
from model.TradingPair import TradingPair, Chain
from tqdm import tqdm
import ccxt

class XT(BaseExchange):

    def __init__(self):
        super().__init__("XT", "xt", "xt")
    
    async def loadTradingPairs(self):
        pairs = {}
        symbols = await self.exchange.fetch_markets()

        currencies = await self.exchange.fetch_currencies()
        for symbol in symbols:
            if symbol["type"] != "spot":
                continue

            if symbol["quote"] == "USDT" and symbol["info"]["state"]=="ONLINE":
                if symbol["base"] not in currencies.keys():
                    continue      
                curChains = currencies[symbol["base"]]["networks"]

                pair = TradingPair(symbol["symbol"], self.configKey , fee=float(symbol["info"]["takerFeeRate"]))
                       
                for key, c in curChains.items():

                    if c["withdraw"]:
                        chain = Chain(key, float(c["fee"]), c["withdraw"], c["deposit"],c["info"]["contract"], float(c["limits"]["withdraw"]["min"]))
                        pair.addChain(chain)

                pairs[pair.symbol] = pair
        
        self.tradingPairs = pairs
    
    async def getPrices(self):

        prices = await self.exchange.fetch_bids_asks()

        for symbol,ticker in prices.items():

            if symbol[-4:].upper() == "USDT":
               
                if symbol in list(self.tradingPairs.keys()):
                    if ticker["ask"]:
                        self.tradingPairs[symbol].buyPrice = float(ticker["ask"])
                        
                    if ticker["bid"]:
                        self.tradingPairs[symbol].sellPrice = float(ticker["bid"])
                    