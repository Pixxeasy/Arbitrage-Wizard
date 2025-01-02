class Chain():

    def __init__(self, name, fee, withdraw, deposit, contractAddress=None, minAmount=0):
        self.name = self._convertChainName(name)
        self.fee = fee 
        self.withdraw = withdraw
        self.deposit = deposit
        self.contractAddress = contractAddress.lower() if contractAddress else ""
        self.minAmount = minAmount

    def _convertChainName(self,name):
        
        return name

class TradingPair():
    def __init__(self, symbol, exchange, sellPrice: float=0, fee: float=0, buyPrice: float=0):
    
        self.symbol = symbol
        self.sellPrice = sellPrice
        self.buyPrice = buyPrice
        self.exchange = exchange
        self.fee = fee
        self.chains = {}

    def addChain(self, chain:Chain):
        self.chains[chain.name] = chain
        
    def getChain(self, chainName:str):
        if chainName in self.chains.keys():
            return self.chains[chainName]
        
        return None