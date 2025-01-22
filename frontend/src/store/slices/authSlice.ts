import { createSlice } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'
import type { RootState } from '../store'

type AuthState = {
    token: string | null
}

export const slice = createSlice({
    name: 'auth',
    initialState: { token: null } as AuthState,
    reducers: {
        setCredentials: (
            state,
            {
                payload: { token },
            }: PayloadAction<{ token: string }>,
        ) => {
            state.token = token
        },
    },
})

export const { setCredentials } = slice.actions

export default slice.reducer

export const selectCurrentUser = (state: RootState) => state.auth.token