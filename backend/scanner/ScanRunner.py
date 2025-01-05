import asyncio
from importlib import import_module
from .util import run_periodic
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from model.exchanges.Bitget import Bitget, BaseExchange
from model.ArbitrageModel import ArbitrageOpportunity, ArbitrageGroup
from dotenv import load_dotenv
import pandas as pd
import tqdm.asyncio as tqdm_aync
from collections import Counter

pd.set_option('display.max_columns', None)

class ScanRunner():
    def __init__(self, interval: float):
        self.interval = interval
        self.exchanges = []
        self.exchangeMap = {}
        self.maxAmount = 1000

    async def checkArbitrage(self):
        timeStart = datetime.now()
        opportunities = []
        
        allPairs = []
        priceTask = []
        for ex in self.exchanges:
            
            priceTask.append(ex.getPrices())
        
            allPairs.extend(list(ex.tradingPairs.keys()))
        
        allPairs = [pair for pair,count in Counter(allPairs).items() if count>1]
        await tqdm_aync.tqdm_asyncio.gather(*priceTask, desc="Load prices")

        op_tasks = []
        for pair in allPairs:
            op_tasks.append(asyncio.create_task(self.findOpportunities(pair)))

        ops = await tqdm_aync.tqdm_asyncio.gather(*op_tasks)
        opportunities = [o for op in ops for o in op]
        
        timeEnd = datetime.now()
        
        if len(opportunities)>0:
            df = pd.DataFrame([ao.toDict() for ao in opportunities])
            print(df.sort_values(by=["minProfit"], ascending=False))
        print(f"Took {(timeEnd-timeStart).total_seconds()} seconds")

    async def start(self, connection, exchangeList):
        self.db = connection.session
        await self.loadExchanges(exchangeList)
        
        self.task = asyncio.create_task(run_periodic(1.0, self.checkArbitrage))
        await self.task

    async def stop(self):
        for ex in self.exchanges:
            await ex.exchange.close()
        self.task.cancel()
        self.db.close()

        try:
            await self.task
        except asyncio.CancelledError:
            pass
        
    async def _loadExchange(self, ex_class):
        instance = ex_class()
        print(f"Load {instance.name} pairs")
        await instance.loadTradingPairs()
        print(f"Finished loading {instance.name} pairs")
        self.exchanges.append(instance)
        self.exchangeMap[instance.configKey] = instance

    async def loadExchanges(self, exchangeList):

        load_dotenv()
        ex_task = []
        for ex in exchangeList:
            try:
                module = import_module(f"model.exchanges.{ex}")
                ex_class = getattr(module,ex)
                if issubclass(ex_class, BaseExchange):
                    ex_task.append(self._loadExchange(ex_class))
                else:
                    print(f"Class {ex} is no subclass of BaseExchange")
                    continue
            except Exception as e:
                print(e.with_traceback())
                print(f"No class {ex} was found")
            
        await asyncio.gather(*ex_task)
        
        try:
            self.db.add_all(self.exchanges)
            self.db.commit()
        except IntegrityError:
            pass


    def getTotalPrice(self, orderList, amount, side, fee):
        amountLeft = amount
        totalPrice = 0
    
        
        for i,o in enumerate(orderList[side]):
            if side=="buy":
                if amountLeft <= o["usdt_amount"]:
                    totalPrice += (amountLeft/o["price"])*(1-fee)
                    return totalPrice, amount/totalPrice
                else:
                    totalPrice += o["qty"] * (1-fee)
                    amountLeft -= o["usdt_amount"]

            elif side=="sell":
                if amountLeft <= o["qty"]:
                    totalPrice += amountLeft*o["price"]*(1-fee)
                    return totalPrice, totalPrice/amount
                else:
                    totalPrice += o["usdt_amount"]*(1-fee)
                    amountLeft -= o["qty"]
                    
        if side == "sell":
            return totalPrice, totalPrice/amount
        elif side == "buy":
            return totalPrice, amount/totalPrice

    
    async def findOpportunities(self, pair):
        
        opportunities = []
        comparePrices = []
        for ex in self.exchanges:
            if pair in list(ex.tradingPairs.keys()):
                comparePrices.append(ex.tradingPairs[pair])
            
         #No common trading pair in 2 exchanges was found
        if len(comparePrices) < 2:
            return opportunities

        #Find best sell und buy price
        sellPrices = sorted(comparePrices, key=lambda s: s.sellPrice, reverse=True)
        buyPrices = sorted(comparePrices, key=lambda s: s.buyPrice)
            
        buy = buyPrices[0]
        sell = sellPrices[0]
        
        if buy.exchange == sell.exchange:
            return opportunities
        if buy.buyPrice==0 or sell.sellPrice==0:
            return opportunities
        if buy.buyPrice*(1+buy.fee) >= sell.sellPrice*(1-sell.fee):
            return opportunities

        #An estimate profit
        profit = ((sell.sellPrice-buy.buyPrice)/buy.buyPrice) * 100.0

        if profit < 0:
            return opportunities

        #Find matching chain
        for cbName in buy.chains:
            cb = buy.chains[cbName]
            cs = sell.getChain(cbName)
            if not cs:
                continue
            #Same coin with same contract
            if cb.contractAddress == cs.contractAddress:
                #Withdraw on buy side and deposit on sell side are possible    
                if cb.withdraw and cs.deposit:

                    #Calculate minimum amount of profit
                    minAmount = self.calculateMinProfitAmount(buy.buyPrice, sell.sellPrice,cb.fee,buy.fee, sell.fee,1)
                    if max(minAmount, cb.fee*buy.buyPrice) > self.maxAmount:
                        continue
                                            
                    #Get orderbook of coin on buy exchange
                    buy_orders = await self.exchangeMap[buy.exchange].getOrders(buy.symbol)
                            
                    #Get all possibilities for buying
                    buy_possibilities = self.calulateBuyPrices(buy_orders,max(minAmount, cb.fee*buy.buyPrice),sell.sellPrice,buy.fee, sell.fee, cb.fee)
                    if len(buy_possibilities) == 0:
                        continue

                    #Get orderbook of coin on sell exchange
                    sell_orders = await self.exchangeMap[sell.exchange].getOrders(sell.symbol)
                            
                    sell_ops = self.findBestSellPrice(buy_possibilities,sell_orders,sell.fee,1.0)

                    if len(sell_ops) == 0:
                        continue

                    ag = ArbitrageGroup(buy.exchange, sell.exchange, pair, cb.name)
                    ag.setOpportunities(sell_ops)
                    opportunities.append(ag)

        return opportunities
    
    def calculateMinProfitAmount(self, buyPrice, sellPrice, withdrawFee, buyFee, sellFee, profit):
        first = withdrawFee * sellPrice * (1 - sellFee)
        second = (1 - buyFee) * sellPrice * (1 - sellFee) / buyPrice - (1+(profit/100))
        
        return first/second

    def _calculateMinBuyAmount(self, sellPrice, withdrawFee, buyFee, buyPrice, amount, level, buyOrders ):

        totalPrice = sum(buyOrders[i]["qty"] for i in range(level+1))
        numerator = sellPrice * totalPrice * (1-buyFee) - amount - sellPrice * withdrawFee
        denominator = (1+ (sellPrice*(1-buyFee)/buyPrice))

        return numerator/denominator



    def calulateBuyPrices(self, buyOrders, amount, sellPrice, buyFee, sellFee, withdrawFee):
        possibilities = []
        buyPrice = buyOrders["buy"][0]["price"]
        sellPrice_with_fee = sellPrice * (1 - sellFee)
        minAmount = amount
        currentAmount = 0

        #Buyprice already too high
        if buyPrice*(1+buyFee)>=sellPrice_with_fee:
            return possibilities

        for i in range(len(buyOrders["buy"])):
            order = buyOrders["buy"][i]
            currentAmount += order["usdt_amount"]
            currentAmount = min(currentAmount, self.maxAmount)
            maxTotal, maxRate = self.getTotalPrice(buyOrders, currentAmount, "buy", buyFee)
            maxRealTotal = maxTotal - withdrawFee
            maxRealRate = currentAmount / maxRealTotal

            if maxRealRate > sellPrice_with_fee:
                continue

            remove_amount = self._calculateMinBuyAmount(sellPrice_with_fee, withdrawFee,buyFee,order["price"],currentAmount,i, buyOrders["buy"])

            if (remove_amount < 0) or (currentAmount-remove_amount < minAmount):
                continue

            minBuyAmount = currentAmount - remove_amount

            minTotal, minRate = self.getTotalPrice(buyOrders, minBuyAmount, "buy", buyFee)
            minRealTotal = minTotal - withdrawFee
            minRealRate = minBuyAmount/ minRealTotal

            if (minRealRate > sellPrice_with_fee):
                continue

            possibilities.append({
                "minAmount": minBuyAmount,
                "maxAmount": currentAmount,
                "minRate": minRate,
                "maxRate": maxRate,
                "minRealTotal": minRealTotal,
                "maxRealTotal": maxRealTotal,
            })

            if currentAmount == self.maxAmount:
                return possibilities
        return possibilities

    def findBestSellPrice(self, buy_possibilities, orders, sell_fee, profit_percent):
        opportunities = []

        for pos in buy_possibilities:
            minRealSellPrice, minRealSellRate = self.getTotalPrice(orders, pos["minRealTotal"], "sell", sell_fee)
            maxRealSellPrice, maxRealSellRate = self.getTotalPrice(orders, pos["maxRealTotal"], "sell", sell_fee)

            minProfit = minRealSellPrice - pos["minAmount"]
            maxProfit = maxRealSellPrice - pos["maxAmount"]

            if (minProfit > pos["minAmount"] * (profit_percent / 100)) and (
                    maxProfit > pos["maxAmount"] * (profit_percent / 100)):
                ao = ArbitrageOpportunity(pos["minAmount"], pos["maxAmount"], minRealSellPrice, maxRealSellPrice,
                                          minProfit, maxProfit, pos["minRate"], minRealSellRate)
                opportunities.append(ao)

        return opportunities