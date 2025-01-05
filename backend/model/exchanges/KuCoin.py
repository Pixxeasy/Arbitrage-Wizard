from .BaseExchange import BaseExchange
import requests
from model.TradingPair import TradingPair, Chain
import os
from kucoin import AsyncClient, KucoinAPIException
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio
from ccxt.base.errors import ExchangeError,InvalidNonce
import asyncio
import time
import ccxt

class KuCoin(BaseExchange):

    def __init__(self):
        super().__init__("KuCoin", "kuc", "kucoin")

        self.exchange.apiKey = self.apiKey
        self.exchange.secret = self.apiSecret
        self.exchange.password = self.passphrase
        self.exchange.adjustForTimeDifference = True


         
        
    async def loadTradingPairs(self):
        pairs = {}

        symbols = await self.exchange.fetch_markets()
        currencies = await self.exchange.fetch_currencies()

        #base_fees = await self.client.get_base_fee()
    
        for symbol in symbols:
            if symbol["type"] != "spot":
                continue

            if symbol["quote"] == "USDT" and symbol["info"]["enableTrading"]:
                if symbol["base"] not in currencies.keys():
                    continue      
                curChains = currencies[symbol["base"]]["networks"]
                pair = TradingPair(symbol["symbol"], self.configKey ,fee=float(symbol["taker"]))
                       
                for key, c in curChains.items():

                    if c["active"]:
                        chain = Chain(key, float(c["fee"]), c["withdraw"], c["deposit"],c["info"]["contractAddress"], float(c["limits"]["withdraw"]["min"]))
                        pair.addChain(chain)

                pairs[pair.symbol] = pair
        
        self.tradingPairs = pairs

    async def getOrders(self, symbol):

        try:
            orderbook = await self.exchange.fetch_order_book(symbol)
        except ExchangeError as e:
            print(e)
            await asyncio.sleep(1)
            return await self.getOrders(symbol)
        except InvalidNonce as In:
            print(In)
            await self.exchange.load_time_difference()
            return await self.getOrders(symbol)

        book = {}
        book["buy"] = []
        book["sell"] = []

        for ask in orderbook["asks"]:
            book["buy"].append({"qty": float(ask[1]), "price": float(ask[0]), "usdt_amount": float(ask[0])*float(ask[1])})

        for bid in orderbook["bids"]:
            book["sell"].append({"qty": float(bid[1]), "price": float(bid[0]), "usdt_amount": float(bid[0])*float(bid[1])})

        return book