from .BaseExchange import BaseExchange
import requests
from model.TradingPair import TradingPair, convertSymbol, Chain
import os
from kucoin import AsyncClient, KucoinAPIException
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio
import asyncio
import time

class KuCoin(BaseExchange):

    isAsync = True

    def __init__(self):
        super().__init__("KuCoin", "kuc")

        print(self.apiKey)
        print(self.apiSecret)
        print(self.passphrase)
        self.client = AsyncClient(self.apiKey, self.apiSecret, self.passphrase)
        
    @classmethod    
    async def create(cls):
        obj = cls()

        obj.tradingPairs = await obj.getAvailablePairs()

        return obj
         
        
    async def getAvailablePairs(self):
        print("Load Trading Pairs of KuCoin")
        pairs = {}
        symbols = await self.client.get_symbols()
        

        currencies = await self.client.get_currencies()

        base_fees = await self.client.get_base_fee()
    
        currency_list = {}
        for entry in currencies:
                coin = entry["currency"]
                currency_list[coin] = entry["chains"]

        symbol_tasks = []
        for symbol in symbols:
            if symbol["quoteCurrency"] == "USDT" and symbol["enableTrading"]:
                symbol_tasks.append(
                    self._loadSymbol(symbol,pairs,currency_list,base_fees)
                )
        
        await tqdm_asyncio.gather(*symbol_tasks)

        return pairs
    
    async def _loadSymbol(self, symbol_dict, pairs, currency_list, base_fees):
        if symbol_dict["baseCurrency"] not in list(currency_list.keys()):
                return
        curChains = currency_list[symbol_dict["baseCurrency"]]

        try:
            fees = await self.client.get_trading_pair_fee([symbol_dict["symbol"]])
        except KucoinAPIException as e:
            print(e)
            return
                    
        print(fees)
                    
        print(symbol_dict["symbol"] + "  completed")
        if len(fees) == 0:
            buyFee = base_fees["makerFeeRate"]
            sellFee = base_fees["takerFeeRate"]
        else:
                        
            buyFee = fees[0]["makerFeeRate"]
            sellFee = fees[0]["takerFeeRate"] 

        print("maker: " + buyFee + ", " + str(float(symbol_dict["makerFeeCoefficient"])*float(base_fees["makerFeeRate"])))
        print("taker: " + sellFee + ", " + str(float(symbol_dict["takerFeeCoefficient"])*float(base_fees["takerFeeRate"])))
           

        pair = TradingPair(symbol_dict["symbol"], self.configKey ,buyFee=buyFee, sellFee=sellFee)
        for c in curChains:
                if c["isWithdrawEnabled"]:
                                
                    chain = Chain(c["chainName"], float(c["withdrawalMinFee"]), c["isWithdrawEnabled"], c["isDepositEnabled"], c["contractAddress"], float(c["withdrawalMinSize"]))
                    pair.addChain(chain)
        pairs[pair.symbol] = pair
        return
        
    def getPrices(self):
        prices = self.market_client.get_all_tickers()["ticker"]

        for symbol in prices:
            if symbol["symbol"][-4:]== "USDT":
                pair = convertSymbol(symbol["symbol"])
                if pair in list(self.tradingPairs.keys()):
                    self.tradingPairs[pair].buyPrice = float(symbol["buy"])
                    self.tradingPairs[pair].sellPrice = float(symbol["sell"])

    def getOrders(self, symbol):
        orders_resp = self.market_client.get_part_order(100,symbol)
        
        book = {}
        book["buy"] = []
        book["sell"] = []
        
        for ask in orders_resp["asks"]:
            book["buy"].append({"qty": float(ask[1]), "price": float(ask[0]), "usdt_amount": float(ask[0])*float(ask[1])})

        for bid in orders_resp["bids"]:
            book["sell"].append({"qty": float(bid[1]), "price": float(bid[0]), "usdt_amount": float(bid[0])*float(bid[1])})

        return book
