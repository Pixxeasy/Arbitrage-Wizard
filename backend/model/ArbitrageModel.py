

class ArbitrageOpportunity:

    def __init__(self, minStartAmount, maxStartAmount, minEndAmount, maxEndAmount, minProfit, maxProfit, buyPrice, sellPrice):
        self.sellPrice = sellPrice
        self.buyPrice = buyPrice
        self.minStartAmount = minStartAmount
        self.maxStartAmount = maxStartAmount
        self.minEndAmount = minEndAmount
        self.maxEndAmount = maxEndAmount
        self.minProfit = minProfit
        self.maxProfit = maxProfit

    def toDict(self):
        return {
            "buyPrice": self.buyPrice,
            "minStartAmount": self.minStartAmount,
            "maxStartAmount": self.maxStartAmount,
            "minEndAmount": self.minEndAmount,
            "maxEndAmount": self.maxEndAmount,
            "minProfit": self.minProfit,
            "maxProfit": self.maxProfit,
            "sellPrice": self.sellPrice
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

    def setOpportunities(self, opportunities):
        self.opportunityList = opportunities

    def toDict(self):
        meanMinStartAmount = sum([o.minStartAmount for o in self.opportunityList]) / len(self.opportunityList)
        meanMaxStartAmount = sum([o.maxStartAmount for o in self.opportunityList]) / len(self.opportunityList)
        meanMinEndAmount = sum([o.minEndAmount for o in self.opportunityList]) / len(self.opportunityList)
        meanMaxEndAmount = sum([o.maxEndAmount for o in self.opportunityList]) / len(self.opportunityList)
        meanMinProfit = sum([o.minProfit for o in self.opportunityList]) / len(self.opportunityList)
        meanMaxProfit = sum([o.maxProfit for o in self.opportunityList]) / len(self.opportunityList)
        meanBuyPrice = sum([o.buyPrice for o in self.opportunityList]) / len(self.opportunityList)
        meanSellPrice = sum([o.sellPrice for o in self.opportunityList]) / len(self.opportunityList)

        return {
            "tradingPair": self.tradingPair,
            "buyExchange": self.buyExchange,
            "buyPrice": meanBuyPrice,
            "minStartAmount": meanMinStartAmount,
            "maxStartAmount": meanMaxStartAmount,
            "minEndAmount": meanMinEndAmount,
            "maxEndAmount": meanMaxEndAmount,
            "chain": self.chain,
            "sellExchange": self.sellExchange,
            "sellPrice": meanSellPrice,
            "minProfit": meanMinProfit,
            "maxProfit": meanMaxProfit,
            "opportunities": len(self.opportunityList)
        }