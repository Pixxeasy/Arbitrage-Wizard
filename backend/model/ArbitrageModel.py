

class ArbitrageOpportunity():

    def __init__(self, sellExchange, buyExchange, sellPrice, buyPrice, profit, tradingPair, chain):
        self.sellExchange = sellExchange
        self.buyExchange = buyExchange
        self.sellPrice = sellPrice
        self.buyPrice = buyPrice
        self.profit = profit
        self.tradingPair = tradingPair
        self.chain = chain
        pass

    def toDict(self):
        return {
            "tradingPair": self.tradingPair,
            "buyExchange": self.buyExchange,
            "buyPrice": self.buyPrice,
            "chain": self.chain,
            "sellExchange": self.sellExchange,
            "sellPrice": self.sellPrice,
            "profit": self.profit
        }