import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import {API_BASE_URL} from "../../util/constants"
import {RootState} from "../store.ts";

// initialize an empty api service that we'll inject endpoints into later as needed
export const baseApi = createApi({
    baseQuery: fetchBaseQuery({ baseUrl: API_BASE_URL+"/api" }),
    reducerPath: "base",

    endpoints: () => ({}),
})

export const protectedBaseApi = createApi({
    baseQuery: fetchBaseQuery(
        {
            baseUrl: API_BASE_URL+"/api" ,
            prepareHeaders: (headers, { getState }) => {
                // By default, if we have a token in the store, let's use that for authenticated requests
                const token = (getState() as RootState).auth.token
                if (token) {
                    headers.set('authorization', `Bearer ${token}`)
                }
                headers.set('Content-Type', 'application/json')
                return headers
            }
        }),
    reducerPath: "protected",
    endpoints: () => ({}),
})

