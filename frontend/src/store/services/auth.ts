import { baseApi } from './base'
import axios from "axios";

export interface UserResponse {
    access_token: string
    token_type: string
}

export interface LoginRequest {
    username: string
    password: string
}

export const authApi = baseApi.injectEndpoints({
    endpoints: (build) => ({
        login: build.mutation<UserResponse, LoginRequest>({
            query: (credentials) => {
                const formData = axios.toFormData(credentials);
                return {
                    url: '/auth/login',
                    method: 'POST',
                    body: formData
                }
            }
        }),
    }),
    overrideExisting: false,
})

export const { useLoginMutation } = authApi
