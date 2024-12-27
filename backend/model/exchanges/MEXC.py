from .BaseExchange import BaseExchange
from model.TradingPair import TradingPair, Chain
from tqdm import tqdm

class MEXC(BaseExchange):

    def __init__(self):
        super().__init__("MEXC", "mxc", "mexc")

        self.exchange.apiKey = self.apiKey
        self.exchange.secret = self.apiSecret
        self.tradingPairs = self.getAvailablePairs()
        
    
        
    def getAvailablePairs(self):
        pairs = {}
        print("Load Trading Pairs of MEXC")
        symbols = self.exchange.fetch_markets()

        currencies = self.exchange.fetch_currencies()

        for symbol in tqdm(symbols):
            if symbol["type"] != "spot":
                continue

            if symbol["quote"] == "USDT" and symbol["active"]:
                if  not currencies[symbol["base"]]:
                    continue      
                curChains = currencies[symbol["base"]]["networks"]
                pair = TradingPair(symbol["symbol"], self.configKey ,buyFee=float(symbol["maker"]), sellFee=float(symbol["taker"]))
                       
                for key, c in curChains.items():

                    if c["withdraw"]:
                        chain = Chain(key, float(c["fee"]), c["withdraw"], c["deposit"],c["info"]["contract"], float(c["limits"]["withdraw"]["min"]))
                        pair.addChain(chain)

                pairs[pair.symbol] = pair
        
        return pairs