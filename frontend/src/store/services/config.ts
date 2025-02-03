import {protectedBaseApi} from "./base.ts";
import { FetchBaseQueryError} from "@reduxjs/toolkit/query";
import {ConfigResponse, ExchangeResponse, UserConfig} from "../../types/UserConfig.ts";

export const configApi = protectedBaseApi.injectEndpoints({
    endpoints: (build) => ({
        getConfigs: build.query({
            async queryFn(_arg, _queryApi, _extraOptions, fetchWithBQ) {
                // get a random user
                const exchangeResponse = await fetchWithBQ('/exchange/available')
                if (exchangeResponse.error)
                    return { error: exchangeResponse.error as FetchBaseQueryError }
                const exchanges: { [key: string]: UserConfig } = {};
                exchangeResponse.data.forEach((item: ExchangeResponse) => {
                    exchanges[item.config_key] = {
                        "maxAmount": 0,
                        "exchangeShort": item.config_key,
                        "exchangeLong": item.name
                    }
                })

                const configResponse = await fetchWithBQ(`/exchange/userConfig`)

                if (configResponse.error)
                    return { error: configResponse.error as FetchBaseQueryError }

                configResponse.data.forEach((item: ConfigResponse) => {
                    const config = exchanges[item.exchange_key]
                    config.maxAmount = item.max_amount
                    config.apiKey = item.api_key
                    config.apiPassphrase = item.api_passphrase
                    config.apiSecret = item.api_secret
                })
                const data = Object.values(exchanges)
                
                return {data}
            }
        }),
        addConfigs: build.mutation<ConfigResponse[], ConfigResponse[]>({
            query: ( configs ) => ({
                url: `/exchange/userConfig/edit`,
                // When performing a mutation, you typically use a method of
                // PATCH/PUT/POST/DELETE for REST endpoints
                method: 'POST',
                // fetchBaseQuery automatically adds `content-type: application/json` to
                // the Headers and calls `JSON.stringify(patch)`
                body: configs,
            }),
        })
    }),
    overrideExisting: false,
})

export const { useGetConfigsQuery, useAddConfigsMutation } = configApi;