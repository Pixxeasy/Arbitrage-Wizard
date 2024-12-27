from .BaseExchange import BaseExchange
import requests
from model.TradingPair import TradingPair, convertSymbol, Chain

class Bitget(BaseExchange):

    def __init__(self):
        super().__init__("Bitget", "btg")

        self.tradingPairs = self.getAvailablePairs()
        
    def getAvailablePairs(self):
        pairs = {}
        symbols_resp = requests.get("https://api.bitget.com/api/v2/spot/public/symbols")

        currency_resp = requests.get("https://api.bitget.com/api/v2/spot/public/coins")


        if symbols_resp.status_code == 200:
            if currency_resp.status_code == 200:
                
                currency_data = currency_resp.json()["data"]
                currency_list = {}
                for entry in currency_data:
                     coin = entry["coin"]
                     currency_list[coin] = entry["chains"]

                for symbol in symbols_resp.json()["data"]:
                    if symbol["quoteCoin"] == "USDT" and symbol["status"]== "online":
                            curChains = currency_list[symbol["baseCoin"]]
                            pair = TradingPair(symbol["symbol"], self.configKey ,buyFee=float(symbol["makerFeeRate"]), sellFee=float(symbol["takerFeeRate"]))
                       
                            for c in curChains:
                                 if c["withdrawable"] == "true":
                                    chain = Chain(c["chain"], float(c["withdrawFee"]), eval(c["withdrawable"].capitalize()), eval(c["rechargeable"].capitalize()),c["contractAddress"], float(c["minWithdrawAmount"]))
                                    pair.addChain(chain)

                            pairs[pair.symbol] = pair
        
        return pairs
    
    def getPrices(self):
         prices_resp = requests.get("https://api.bitget.com/api/v2/spot/market/tickers")

         if prices_resp.status_code == 200:
              for symbol in prices_resp.json()["data"]:
                   if symbol["symbol"][-4:].upper() == "USDT":
                    pair = convertSymbol(symbol["symbol"])
                    if pair in list(self.tradingPairs.keys()):
                        self.tradingPairs[pair].buyPrice = float(symbol["askPr"])
                        self.tradingPairs[pair].sellPrice = float(symbol["bidPr"])

    def getOrders(self, symbol):
        orders_resp = requests.get("https://api.bitget.com/api/v2/spot/market/orderbook", params={"symbol": symbol})
        orders_json = orders_resp.json()["data"]
        book = {}
        book["buy"] = []
        book["sell"] = []

        for ask in orders_json["asks"]:
            book["buy"].append({"qty": float(ask[0]), "price": float(ask[1]), "usdt_amount": float(ask[0])*float(ask[1])})

        for bid in orders_json["bids"]:
            book["sell"].append({"qty": float(bid[0]), "price": float(bid[1]), "usdt_amount": float(bid[0])*float(bid[1])})

        return book
