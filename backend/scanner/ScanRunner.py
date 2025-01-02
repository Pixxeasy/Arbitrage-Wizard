import asyncio
from importlib import import_module
from .util import run_periodic
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from model.exchanges.Bitget import Bitget, BaseExchange
from model.ArbitrageModel import ArbitrageOpportunity
from dotenv import load_dotenv
import pandas as pd
import tqdm.asyncio as tqdm_aync
from collections import Counter

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
            print(df.sort_values(by=["profit"], ascending=False))
        print(f"Took {(timeEnd-timeStart).total_seconds()} seconds")

    async def start(self, connection, exchangeList):
        self.db = connection.session
        await self.loadExchanges(exchangeList)
        
        self.task = asyncio.create_task(run_periodic(1.0, self.checkArbitrage))

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
                    totalPrice = totalPrice
                    return totalPrice, amount/totalPrice, i
                else:
                    totalPrice += o["qty"] * (1-fee)
                    amountLeft -= o["usdt_amount"]

            elif side=="sell":
                if amountLeft <= o["qty"]:
                    totalPrice += amountLeft*o["price"]*(1-fee)
                    return totalPrice, totalPrice/amount, i
                else:
                    totalPrice += o["usdt_amount"]*(1-fee)
                    amountLeft -= o["qty"]
                    
        if side == "sell":
            return totalPrice, totalPrice/amount, i
        elif side == "buy":
            return totalPrice, amount/totalPrice, i

    
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
                        return opportunities
                                            
                    #Get orderbook of coin on buy exchange       
                    buy_orders = await self.exchangeMap[buy.exchange].getOrders(buy.symbol)
                            
                    #Get all possibilities for buying
                    buy_possibilities = self.calulateBuyPrices(buy_orders,max(minAmount, cb.fee*buy.buyPrice),sell.sellPrice,buy.fee, sell.fee, cb.fee)
                            
                    #Get orderbook of coin on sell exchange
                    sell_orders = await self.exchangeMap[sell.exchange].getOrders(sell.symbol)
                            
                    sell_ops = self.findBestSellPrice(buy_possibilities,sell_orders,sell.fee,1.0)
                            
                    for op in sell_ops:
                        ao = ArbitrageOpportunity(sell.exchange,buy.exchange,op["sell_price"], op["buy_price"], op["profit"], pair,cb.name, op["usdt_amount_start"])
                        opportunities.append(ao)

        return opportunities
    
    def calculateMinProfitAmount(self, buyPrice, sellPrice, withdrawFee, buyFee, sellFee, profit):
        first = withdrawFee * sellPrice * (1 - sellFee)
        second = (1 - buyFee) * sellPrice * (1 - sellFee) / buyPrice - (1+(profit/100))
        
        return first/second
    
    def calulateBuyPrices(self, buyOrders, amount, sellPrice, buyFee, sellFee, withdrawFee):
        possibilities = []
        startAmount = amount
        
        buyPrice = buyOrders["buy"][0]["price"]
        
        #Buyprice already too high
        if buyPrice*(1+buyFee)>=sellPrice*(1-sellFee):
            return possibilities
        
        #Get initial price and rate        
        total, rate, level = self.getTotalPrice(buyOrders,amount,"buy", buyFee)
        initAmount = sum([buyOrders["buy"][i]["usdt_amount"] for i in range(level)])
        realPrice = total - withdrawFee
        realRate = amount/realPrice
        
        if realRate > sellPrice:
            return possibilities
        
        if realPrice > 0:
            possibilities.append({"real_price": realPrice, "rate": rate, "amount": amount})
        
        amount = initAmount
        for i in range(level, len(buyOrders["buy"])):
            o = buyOrders["buy"][i]
            currentAmount = min(amount+o["usdt_amount"],self.maxAmount)
            
            total, rate, level = self.getTotalPrice(buyOrders, currentAmount, "buy", buyFee)
            realPrice = total - withdrawFee
            realRate = currentAmount/realPrice
                
            if realRate > sellPrice:
                if level>0:
                    numerator = sellPrice * sum([buyOrders["buy"][i]["qty"] for i in range(level)]) - amount - sellPrice * withdrawFee
                    denominator = 1 - (sellPrice * (1 - buyFee) / o["price"])
                else:
                    numerator = - sellPrice * withdrawFee
                    denominator = 1 - (sellPrice*((1-buyFee)/o["price"]))                
                
                add_amount = numerator/denominator
                if add_amount > o["usdt_amount"]:
                    amount += o["usdt_amount"]
                    continue
                if add_amount < 0:
                    return possibilities
                
                amount += add_amount
                currentAmount = min(amount, self.maxAmount)
                total, rate, level = self.getTotalPrice(buyOrders, currentAmount, "buy", buyFee)
                realPrice = total - withdrawFee
                realRate = currentAmount/realPrice
                if realRate < sellPrice:
                    possibilities.append({"real_price": realPrice, "rate": rate, "amount": currentAmount})
                return possibilities
            
            elif currentAmount == self.maxAmount:
                possibilities.append({"real_price": realPrice, "rate": rate, "amount": currentAmount})
                return possibilities

            possibilities.append({"real_price": realPrice, "rate": rate, "amount": currentAmount})
            amount += o["usdt_amount"]
    
    def findBestSellPrice(self, buy_possibilities, orders, sell_fee, profit_percent):
        possibilities = []
        
        for pos in sorted(buy_possibilities, key=lambda p: p["real_price"], reverse=True):
            real_sell_price, sell_rate,i = self.getTotalPrice(orders,pos["real_price"], "sell", sell_fee)

            
            real_profit = real_sell_price - pos["amount"]
            if real_profit > pos["amount"] * (profit_percent/100):
                possibilities.append({"profit": real_profit, "usdt_amount_end": real_sell_price, "usdt_amount_start": pos["amount"], "buy_price": pos["rate"], "sell_price": sell_rate})
                
        return possibilities

            
            