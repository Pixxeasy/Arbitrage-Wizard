import { configureStore } from "@reduxjs/toolkit";
import {authApi} from "./services/auth.ts";
import {arbitrageApi}from "./services/arbitrage.ts";
import {slice} from "./slices/authSlice"
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux'

const store = configureStore({
    reducer: {
        [authApi.reducerPath]: authApi.reducer,
        [arbitrageApi.reducerPath]: arbitrageApi.reducer,
        auth: slice.reducer,
    },
    middleware: (getDefaultMiddleware) =>
        getDefaultMiddleware().concat(authApi.middleware).concat(arbitrageApi.middleware),
});

export default store;
export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
export const useTypedSelector: TypedUseSelectorHook<RootState> = useSelector
export const useAppDispatch = () => useDispatch<AppDispatch>()