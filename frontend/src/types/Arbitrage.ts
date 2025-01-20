export interface ArbitrageGroup {
    buyExchange?: string,
    sellExchange?: string,
    tradingPair: string,
    chainName: string,
    opportunities: ArbitrageOpportunity[]
}

export interface ArbitrageOpportunity {
    minAmountStart?: number;
    maxAmountStart?: number;
    minAmountEnd?: number;
    maxAmountEnd?: number;
    minProfit?: number;
    maxProfit?: number;
    buyPrice: number;
    sellPrice: number;
}
