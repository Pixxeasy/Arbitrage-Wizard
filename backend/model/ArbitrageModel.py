

class ArbitrageOpportunity:

    def __init__(self, sellExchange, buyExchange, sellPrice, buyPrice, profit, tradingPair, chain, usdtAmount):
        self.sellExchange = sellExchange
        self.buyExchange = buyExchange
        self.sellPrice = sellPrice
        self.buyPrice = buyPrice
        self.profit = profit
        self.tradingPair = tradingPair
        self.chain = chain
        self.ustdAmount = usdtAmount
        pass

    def toDict(self):
        return {
            "tradingPair": self.tradingPair,
            "buyExchange": self.buyExchange,
            "buyPrice": self.buyPrice,
            "chain": self.chain,
            "sellExchange": self.sellExchange,
            "sellPrice": self.sellPrice,
            "profit": self.profit,
            "usdtAmount": self.ustdAmount
        }

class ArbitrageGroup:
    def __init__(self, buyExchange, sellExchange, tradingPair, chain):
        self.buyExchange = buyExchange
        self.sellExchange = sellExchange
        self.tradingPair = tradingPair
        self.chain = chain
        self.opportunityList = []

    def addOpportunity(self, opportunity: ArbitrageOpportunity):
        self.opportunityList.append(opportunity)

    def toDict(self):
        meanUsdtAmount = sum([o.ustdAmount for o in self.opportunityList]) / len(self.opportunityList)
        meanProfit = sum([o.profit for o in self.opportunityList]) / len(self.opportunityList)
        meanBuyPrice = sum([o.buyPrice for o in self.opportunityList]) / len(self.opportunityList)
        meanSellPrice = sum([o.sellPrice for o in self.opportunityList]) / len(self.opportunityList)

        return {
            "tradingPair": self.tradingPair,
            "buyExchange": self.buyExchange,
            "buyPrice": meanBuyPrice,
            "chain": self.chain,
            "sellExchange": self.sellExchange,
            "sellPrice": meanSellPrice,
            "profit": meanProfit,
            "usdtAmount": meanUsdtAmount,
            "opportunities": len(self.opportunityList)
        }