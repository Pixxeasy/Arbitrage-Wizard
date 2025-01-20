import { configureStore } from "@reduxjs/toolkit";
import { LoginSlice } from "./slices/LoginSlice";
import {CurrentArbitrageSlice} from "./slices/ArbitrageSlice"

const store = configureStore({
    reducer: {
        login: LoginSlice.reducer,
        currentArbitrage: CurrentArbitrageSlice.reducer,
    },
    middleware: (getDefaultMiddleware) =>
        getDefaultMiddleware({
            immutableCheck: false,
            serializableCheck: false
        })
});

export default store;