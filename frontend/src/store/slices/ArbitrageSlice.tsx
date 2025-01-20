import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import axios from "axios";
import {API_BASE_URL} from "../../config/constants"
import {ArbitrageGroup} from "../../types/Arbitrage.ts";

// Define the initial state type
interface FetchState {
    arbitrageGroups: ArbitrageGroup[];
    lastUpdate: number;
    isFetching: boolean;
    isSuccess: boolean;
    isError: boolean;
    errorMessage: string;
}

// Define the async thunk for login
export const getArbitrage = createAsyncThunk<
    {lastUpdate: number, arbitrages: ArbitrageGroup[]}, // The type of the data returned when the async action is fulfilled
    void,  // The type of the argument the async action accepts
    { rejectValue: { message: string } }>(
    "arbitrage/current",
    async (_,thunkAPI) => {
        try {

            const link = API_BASE_URL + "/api/arbitrage/current";
            const response = await axios.get(
                link,
                { headers: { "Content-Type": "application/json",
                    "Authorization": `Bearer ${sessionStorage.getItem("token")}` }
                });
            const data = response.data;

            if (response.status === 200) {
                const groups: ArbitrageGroup[] = data.arbitrages.map(item => {
                    return {
                        "buyExchange": item.buy_exchange_name,
                        "sellExchange": item.sell_exchange_name,
                        "tradingPair": item.trading_pair,
                        "chainName": item.chain,
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
                const utcDate = new Date(data.last_update);
                const timezoneOffset = utcDate.getTimezoneOffset() * 60;
                const localTimestamp = data.last_update - timezoneOffset;

                return {lastUpdate: localTimestamp, arbitrages: groups};
            } else {
                return thunkAPI.rejectWithValue(data.detail);
            }
        } catch (e: any) {
            if (axios.isAxiosError(e)) {
                console.log("Error", e.response?.data);
                return thunkAPI.rejectWithValue(e.response?.data);
            }
            else {
                return thunkAPI.rejectWithValue(e);
            }
        }
    }
);

// Define the slice
export const CurrentArbitrageSlice = createSlice({
    name: "currentArbitrage",
    initialState: {
        arbitrageGroups: [],
        lastUpdate: Date.now(),
        isFetching: false,
        isSuccess: false,
        isError: false,
        errorMessage: ""
    } as FetchState,
    reducers: {
        clearState: (state) => {
            state.isError = false;
            state.isSuccess = false;
            state.isFetching = false;
        }
    },
    extraReducers: (builder) => {
        builder
            .addCase(getArbitrage.fulfilled, (state, action: PayloadAction<{lastUpdate: number, arbitrages: ArbitrageGroup[]}>) => {
                state.arbitrageGroups = action.payload.arbitrages;
                state.lastUpdate = action.payload.lastUpdate;
                state.isFetching = false;
                state.isSuccess = true;
            })
            .addCase(getArbitrage.rejected, (state, action: PayloadAction<{ message: string } | undefined>) => {
                state.isFetching = false;
                state.isError = true;
                state.errorMessage = action.payload?.message || "An error occurred.";
            })
            .addCase(getArbitrage.pending, (state) => {
                state.isFetching = true;
            });
    }
});

// Export actions and selectors
export const { clearState } = CurrentArbitrageSlice.actions;

export const arbitrageSelector = (state: { currentArbitrage: FetchState }) => state.currentArbitrage;
