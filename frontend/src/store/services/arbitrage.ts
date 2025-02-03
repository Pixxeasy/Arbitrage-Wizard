import {protectedBaseApi} from "./base.ts";
import {
    ArbitrageGroup,
    CurrentArbitrageResponse,
    ArbitrageGroupResponse,
    HistoricArbitrage, HistoricArbitrageResponse
} from "../../types/Arbitrage.ts";

export const arbitrageApi = protectedBaseApi.injectEndpoints({
    endpoints: (build) => ({
        currentArbitrages: build.query({
            query: () => "/arbitrage/current",
            transformResponse(response: CurrentArbitrageResponse): Promise<{lastUpdate: number, arbitrages: ArbitrageGroup[], clientTime: number}> | never {
                if (response?.detail) {
                    throw new Error(response.detail);
                }

                if (!response?.arbitrages) {
                    throw new Error("Server response malformed");
                }

                if (!response?.last_update) {
                    throw new Error("Server response malformed");
                }

                const groups: ArbitrageGroup[] = response.arbitrages.map((item: ArbitrageGroupResponse) => {
                    return {
                        "buyExchange": item.buy_exchange_name,
                        "sellExchange": item.sell_exchange_name,
                        "tradingPair": item.trading_pair,
                        "chainName": item.chain_name,
                        "opportunities": item.opportunities.map(item => {
                            return {
                                "buyPrice": item.buy_price,
                                "sellPrice": item.sell_price,
                                "minAmountStart": item.min_usdt_start,
                                "minAmountEnd": item.min_usdt_end,
                                "maxAmountStart": item.max_usdt_start,
                                "maxAmountEnd": item.max_usdt_end,
                                "minProfit": item.min_profit,
                                "maxProfit": item.max_profit
                            }
                        })
                    }
                })

                return {lastUpdate: response.last_update*1000, arbitrages: groups, clientTime: Date.now()};
            }
        }),
        historicArbitrages: build.query({
            query: () => "/arbitrage/history",
            transformResponse(response: HistoricArbitrageResponse[]): HistoricArbitrage[] {
                if (response?.detail) {
                    throw new Error(response.detail);
                }

                const history: HistoricArbitrage[] = response.map((item: HistoricArbitrageResponse) => {
                    return {
                        "buyExchange": item.buy_exchange_name,
                        "sellExchange": item.sell_exchange_name,
                        "tradingPair": item.trading_pair,
                        "start": item.series_start*1000,
                        "end": item.series_end*1000,
                        "runs": item.num_runs,
                        "runTime": item.series_end - item.series_start
                    }
                })

                history.sort((a,b) => b.start - a.start)

                return history
            }
        })
    }),
    overrideExisting: false,
})

export const { useCurrentArbitragesQuery, useHistoricArbitragesQuery} = arbitrageApi