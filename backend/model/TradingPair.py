def convertChainName(name: str):
    if "BNB" in name:
        return "BEP20"
    
    if "Ethereum" in name:
        return "ERC20"
    
    if "Polygon" in name:
        return "POL"
    
    return name

class Chain():

    def __init__(self, name, fee, withdraw, deposit, contractAddress=None, minAmount=0):
        self.name = self._convertChainName(name)
        self.fee = fee 
        self.withdraw = withdraw
        self.deposit = deposit
        self.contractAddress = contractAddress if contractAddress else ""
        self.minAmount = minAmount

    def _convertChainName(self,name):
        if "BNB" in name:
            return "BEP20"
    
        if "Ethereum" in name:
            return "ERC20"
    
        if "Polygon" in name:
            return "POL"
        
        if "Solana" in name:
            return "SOL"
        
        if "Arbitrum" in name:
            return "ARB"
    
        if "Tron" in name:
            return "TRC20"
        
        if "Toncoin" in name:
            return "TON"
        return name

class TradingPair():
    def __init__(self, symbol, exchange, sellPrice: float=0, buyFee: float=0, sellFee: float=0, buyPrice: float=0):
    
        self.symbol = symbol
        self.sellPrice = sellPrice
        self.buyPrice = buyPrice
        self.exchange = exchange
        self.buyFee = buyFee
        self.sellFee = sellFee
        self.chains = []

    def addChain(self, chain:Chain):
        self.chains.append(chain) 