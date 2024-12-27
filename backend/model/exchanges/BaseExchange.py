
from sqlalchemy import Column, Integer, String

from model.BaseModel import Base
import uuid
import os
import ccxt

namespace = uuid.UUID("1b4b0697-54a1-4e3b-b3c4-ca83f29e2499")

class BaseExchange(Base):
    __tablename__ = 'exchanges'

    guid = Column(String, primary_key=True)
    name = Column(String)
    configKey = Column(String)

    isAsync = False

    def __init__(self, name: str, configKey, ccxt_id):
        self.name = name
        self.configKey = configKey
        self.guid = str(uuid.uuid5(namespace, f"exchange:{configKey}"))
        self.tradingPairs = []
        self.apiKey = os.getenv(f"{name.upper()}_API_KEY")
        self.apiSecret = os.getenv(f"{name.upper()}_API_SECRET")
        self.passphrase = os.getenv(f"{name.upper()}_API_PASSPHRASE")
        self.exchange = getattr(ccxt, ccxt_id)()
        
        self.markets = self.exchange.load_markets()

    def getPrices(self):
        if not self.exchange.has['fetchTickers']:
            print("Exchange " + self.name + " does not support ticker")
        prices = self.exchange.fetch_tickers()

        for symbol,ticker in prices.items():

            if symbol[-4:].upper() == "USDT":
               
                if symbol in list(self.tradingPairs.keys()):
                    if not ticker["ask"] or not ticker["bid"]:
                        continue

                    self.tradingPairs[symbol].buyPrice = float(ticker["ask"])
                    self.tradingPairs[symbol].sellPrice = float(ticker["bid"])

    
    def getOrders(self, symbol):
        orderbook = self.exchange.fetch_order_book(symbol)

        book = {}
        book["buy"] = []
        book["sell"] = []

        for ask in orderbook["asks"]:
            book["buy"].append({"qty": float(ask[1]), "price": float(ask[0]), "usdt_amount": float(ask[0])*float(ask[1])})

        for bid in orderbook["bids"]:
            book["sell"].append({"qty": float(bid[1]), "price": float(bid[0]), "usdt_amount": float(bid[0])*float(bid[1])})

        return book