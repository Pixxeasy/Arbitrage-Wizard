from .BaseExchange import BaseExchange
import requests
from model.TradingPair import TradingPair, convertSymbol, Chain
import os
from pymexc import spot

class MEXC(BaseExchange):

    def __init__(self):
        super().__init__("MEXC", "mxc")

        self.client = spot.HTTP(api_key = os.getenv("MEXC_API_KEY"), api_secret = os.getenv("MEXC_API_SECRET"))
        self.tradingPairs = self.getAvailablePairs()
        
    
        
    def getAvailablePairs(self):
        pairs = {}
        symbols = self.client.exchange_info()


        currencies = self.client.get_currency_info()
        
                
      
        currency_list = {}
        for entry in currencies:
                coin = entry["coin"]
                currency_list[coin] = entry["networkList"]

        
        for symbol in symbols["symbols"]:
            if symbol["quoteAsset"] == "USDT" and symbol["status"]== "1":
                    if symbol["baseAsset"] not in list(currency_list.keys()):
                             continue
                    curChains = currency_list[symbol["baseAsset"]]

                    pair = TradingPair(symbol["symbol"], self.configKey ,buyFee=float(symbol["makerCommission"]), sellFee=float(symbol["takerCommission"]))
                    for c in curChains:
                            if c["withdrawEnable"]:
                                
                                chain = Chain(c["network"], float(c["withdrawFee"]), c["withdrawEnable"], c["depositEnable"], c["contract"], float(c["withdrawMin"]))
                                pair.addChain(chain)
                    pairs[pair.symbol] = pair
        
        return pairs
    
    def getPrices(self):
        prices = self.client.ticker_book_price()

        for symbol in prices:
            if symbol["symbol"][-4:]== "USDT":
                pair = convertSymbol(symbol["symbol"])
                if pair in list(self.tradingPairs.keys()):
                    self.tradingPairs[pair].buyPrice = float(symbol["askPrice"])
                    self.tradingPairs[pair].sellPrice = float(symbol["bidPrice"])

    def getOrders(self, symbol):
        orders_resp = self.client.order_book(symbol)
        
        book = {}
        book["buy"] = []
        book["sell"] = []
        
        for ask in orders_resp["asks"]:
            book["buy"].append({"qty": float(ask[1]), "price": float(ask[0]), "usdt_amount": float(ask[0])*float(ask[1])})

        for bid in orders_resp["bids"]:
            book["sell"].append({"qty": float(bid[1]), "price": float(bid[0]), "usdt_amount": float(bid[0])*float(bid[1])})

        return book
