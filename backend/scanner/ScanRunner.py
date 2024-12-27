import asyncio
from importlib import import_module
from .util import run_periodic
from sqlalchemy.exc import IntegrityError

from model.exchanges.Bitget import Bitget, BaseExchange
from model.ArbitrageModel import ArbitrageOpportunity
from dotenv import load_dotenv
import pandas as pd

class ScanRunner():
    def __init__(self, interval: float):
        self.interval = interval
        self.exchanges = []
        self.exchangeMap = {}

    async def checkArbitrage(self):

        amount = 50
        opportunities = []
        
        allPairs = []
        for ex in self.exchanges:
            ex.getPrices()
            allPairs.extend(list(ex.tradingPairs.keys()))
        
        allPairs = list(set(allPairs))

        op_tasks = []
        for pair in allPairs:
            op_tasks.append(asyncio.create_task(self.findOpportunities(pair,amount)))

        ops = await asyncio.gather(*op_tasks)
        opportunities = [o for op in ops for o in op]
        
        if len(opportunities)>0:
            df = pd.DataFrame([ao.toDict() for ao in opportunities])
            print(df.sort_values(by=["profit"], ascending=False))

    async def start(self, connection, exchangeList):
        self.db = connection.session
        await self.loadExchanges(exchangeList)
        
        self.task = asyncio.create_task(run_periodic(1.0, self.checkArbitrage))

    async def stop(self):
        self.task.cancel()
        self.db.close()

        try:
            await self.task
        except asyncio.CancelledError:
            pass

    async def loadExchanges(self, exchangeList):

        load_dotenv()
        for ex in exchangeList:
            try:
                module = import_module(f"model.exchanges.{ex}")
                ex_class = getattr(module,ex)
                if issubclass(ex_class, BaseExchange):
                    if ex_class.isAsync:
                        instance = await ex_class.create()
                        print(instance)
                    else:
                        instance = ex_class()
                    self.exchanges.append(instance)
                    self.exchangeMap[instance.configKey] = instance
                else:
                    print(f"Class {ex} is no subclass of BaseExchange")
                    continue
            except Exception as e:
                print(e.with_traceback())
                print(f"No class {ex} was found")
        
        try:
            self.db.add_all(self.exchanges)
            self.db.commit()
        except IntegrityError:
            pass


    def getTotalPrice(self, orderList, amount, side):
        amountLeft = amount
        totalPrice = 0
        
        for o in orderList[side]:
            if side=="buy":
                if amountLeft < o["usdt_amount"]:
                    totalPrice += amountLeft/o["price"]
                    break
                else:
                    totalPrice += o["usdt_amount"]/o["price"]
                    amountLeft -= o["usdt_amount"]

            elif side=="sell":
                if amountLeft < o["qty"]:
                    totalPrice += amountLeft*o["price"]
                    break
                else:
                    totalPrice += o["qty"]*o["price"]
                    amountLeft -= o["qty"]
        if side=="buy":
            return totalPrice, amount/totalPrice
        else:
            return totalPrice, totalPrice/amount

        
    
    async def findOpportunities(self, pair, amount):
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
        if buy.buyPrice==0 or sell.sellPrice==0:
            return opportunities

        #An estimate profit
        profit = ((sell.sellPrice-buy.buyPrice)/buy.buyPrice) * 100.0
            
        if profit < 1:
            return opportunities

        #Find matching chain
        for cb in buy.chains:
            for cs in sell.chains:
                #Chain matches
                if cb.name== cs.name:
                    #Same coin with same contract
                    if cb.contractAddress == cs.contractAddress:
                        #Withdraw on buy side and deposit on sell side are possible    
                        if cb.withdraw and cs.deposit:

                            #Get orderbook of coin on buy exchange       
                            buy_orders = self.exchangeMap[buy.exchange].getOrders(buy.symbol)
                        
                            #Get coins after buy
                            buy_coins, buy_rate = self.getTotalPrice(buy_orders,amount, "buy")
                                    
                            #Coin Amount is not withdrawable
                            if buy_coins*(1-buy.buyFee) < cb.minAmount:
                                continue

                            #Calculate coins after buyFee and withDraw fee (the amount deposited to sell exchange)
                            real_buy_price = buy_coins * (1-buy.buyFee) - cb.fee
                            
                            #Get orderbook of coin on sell exchange
                            sell_orders = self.exchangeMap[sell.exchange].getOrders(sell.symbol)
                            
                            #Get amount of usdt after sell
                            sell_coins, sell_rate = self.getTotalPrice(sell_orders,real_buy_price, "sell")

                            #Calculate with sellFee
                            real_sell_price = sell_coins * (1-sell.sellFee)

                            #Get the profit in usdt
                            real_profit = real_sell_price - amount

                            if real_profit > 0.1:
                                ao = ArbitrageOpportunity(sell.exchange,buy.exchange,sell_rate, buy_rate, real_profit, pair,cb.name)
                                opportunities.append(ao)

        return opportunities
            