from .BaseExchange import BaseExchange
from model.TradingPair import TradingPair, Chain
from tqdm import tqdm

class MEXC(BaseExchange):

    def __init__(self):
        super().__init__("MEXC", "mxc", "mexc")

        self.exchange.apiKey = self.apiKey
        self.exchange.secret = self.apiSecret
        self.exchange.enableRateLimit = True
    async def loadTradingPairs(self):
        pairs = {}
        print("Load Trading Pairs of MEXC")
        symbols = await self.exchange.fetch_markets()
        
        currencies = await self.exchange.fetch_currencies()

        for symbol in symbols:
            if symbol["type"] != "spot":
                continue

            if symbol["quote"] == "USDT" and symbol["info"]["status"]=="1":
                if symbol["base"] not in currencies.keys():
                    continue      
                curChains = currencies[symbol["base"]]["networks"]
                pair = TradingPair(symbol["symbol"], self.configKey , fee=float(symbol["taker"]))
                       
                for key, c in curChains.items():

                    if c["withdraw"]:
                        chain = Chain(key, float(c["fee"]), c["withdraw"], c["deposit"],c["info"]["contract"], float(c["limits"]["withdraw"]["min"]))
                        pair.addChain(chain)

                pairs[pair.symbol] = pair
        
        self.tradingPairs = pairs