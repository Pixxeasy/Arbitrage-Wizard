import {protectedBaseApi} from "./base.ts";
import {ArbitrageGroup, CurrentArbitrageResponse, ArbitrageGroupResponse} from "../../types/Arbitrage.ts";

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
                const utcDate = new Date(response.last_update);
                const timezoneOffset = utcDate.getTimezoneOffset() * 60;
                const localTimestamp = response.last_update - timezoneOffset;

                return {lastUpdate: localTimestamp, arbitrages: groups, clientTime: Date.now()};
            }
        }),
    }),
    overrideExisting: false,
})

export const { useCurrentArbitragesQuery } = arbitrageApi