from .BaseExchange import BaseExchange
import requests
from model.TradingPair import TradingPair, convertSymbol, Chain

class XT(BaseExchange):

    def __init__(self):
        super().__init__("XT", "xt")

        self.tradingPairs = self.getAvailablePairs()
    
    def getAvailablePairs(self):
        pairs = {}

        symbols_resp = requests.get("https://sapi.xt.com/v4/public/symbol")

        currency_resp = requests.get("https://sapi.xt.com/v4/public/wallet/support/currency")

        if symbols_resp.status_code == 200:
            if currency_resp.status_code == 200:
                
                currency_data = currency_resp.json()["result"]
                currency_list = {}
                for entry in currency_data:
                     coin = entry["currency"]
                     currency_list[coin] = entry["supportChains"]


                for symbol in symbols_resp.json()["result"]["symbols"]:
                    if symbol["quoteCurrency"] == "usdt" and symbol["state"]=="ONLINE":
                    
                        pair = TradingPair(symbol["symbol"], self.configKey,buyFee=float(symbol["makerFeeRate"]), sellFee=float(symbol["takerFeeRate"]))
                        if symbol["baseCurrency"] not in list(currency_list.keys()):
                             continue
                        curChains = currency_list[symbol["baseCurrency"]]

                        for c in curChains:
                                 if c["withdrawEnabled"]:
                                    chain = Chain(c["chain"], float(c["withdrawFeeAmount"]),c["withdrawEnabled"], c["depositEnabled"], c["contract"], float(c["withdrawMinAmount"]) )
                                    pair.addChain(chain)
                        pairs[pair.symbol] = pair
        
        return pairs

    def getPrices(self):
        prices_resp = requests.get("https://sapi.xt.com/v4/public/ticker")
        if prices_resp.status_code == 200:
            for symbol in prices_resp.json()["result"]:
                   if symbol["s"][-4:] == "usdt":
                    pair = convertSymbol(symbol["s"])
                 
                    if pair in list(self.tradingPairs.keys()) and symbol["bp"] and symbol["ap"]:
                        
                        self.tradingPairs[pair].sellPrice = float(symbol["bp"])
                        self.tradingPairs[pair].buyPrice = float(symbol["ap"])

    def getOrders(self, symbol):
        orders_resp = requests.get("https://sapi.xt.com/v4/public/depth", params={"symbol": symbol})
        orders_json = orders_resp.json()["result"]
        book = {}
        book["buy"] = []
        book["sell"] = []

        for ask in orders_json["asks"]:
            book["buy"].append({"qty": float(ask[1]), "price": float(ask[0]), "usdt_amount": float(ask[0])*float(ask[1])})

        for bid in orders_json["bids"]:
            book["sell"].append({"qty": float(bid[1]), "price": float(bid[0]), "usdt_amount": float(bid[0])*float(bid[1])})

        return book