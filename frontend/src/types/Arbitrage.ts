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

export interface CurrentArbitrageResponse {
    detail?: string
    last_update?: number
    arbitrages?: []
}

export interface ArbitrageGroupResponse {
    buy_exchange_name: string,
    sell_exchange_name: string,
    trading_pair: string,
    chain_name: string,
    opportunities: ArbitrageOpportunityResponse[]
}

export interface ArbitrageOpportunityResponse {
    min_usdt_start: number;
    max_usdt_start: number;
    min_usdt_end: number;
    max_usdt_end?: number;
    min_profit?: number;
    max_profit?: number;
    buy_price: number;
    sell_price: number;
}
