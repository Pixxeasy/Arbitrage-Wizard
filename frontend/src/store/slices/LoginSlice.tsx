import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import axios from "axios";
import {API_BASE_URL} from "../../config/constants"

// Define types for the login response data
interface LoginResponse {
    access_token: string;
}

// Define types for the login request data
interface LoginRequest {
    username: string;
    password: string;
}

// Define the initial state type
interface LoginState {
    token: string;
    isFetching: boolean;
    isSuccess: boolean;
    isError: boolean;
    errorMessage: string;
}

// Define the async thunk for login
export const loginUser = createAsyncThunk<
    LoginResponse, // The type of the data returned when the async action is fulfilled
    LoginRequest,  // The type of the argument the async action accepts
    { rejectValue: { message: string } } // The type of data returned when the async action is rejected
>(
    "users/login",
    async ({ username, password }, thunkAPI) => {
        try {

            const formData = axios.toFormData({"username": username, "password": password});
            const link = API_BASE_URL + "/api/auth/login";
            const response = await axios.post(
                link,
                formData,
                { headers: { "Content-Type": "multipart/form-data" }
            });
            const data = response.data;
            if (response.status === 200) {
                const resp: LoginResponse = data
                sessionStorage.setItem("token", resp.access_token)
                return resp;
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
export const LoginSlice = createSlice({
    name: "login",
    initialState: {
        token: "",
        isFetching: false,
        isSuccess: false,
        isError: false,
        errorMessage: ""
    } as LoginState,
    reducers: {
        clearState: (state) => {
            state.isError = false;
            state.isSuccess = false;
            state.isFetching = false;
        }
    },
    extraReducers: (builder) => {
        builder
            .addCase(loginUser.fulfilled, (state, action: PayloadAction<LoginResponse>) => {
                state.token = action.payload.access_token;
                state.isFetching = false;
                state.isSuccess = true;
            })
            .addCase(loginUser.rejected, (state, action: PayloadAction<{ message: string } | undefined>) => {
                state.isFetching = false;
                state.isError = true;
                state.errorMessage = action.payload?.message || "An error occurred.";
            })
            .addCase(loginUser.pending, (state) => {
                state.isFetching = true;
            });
    }
});

// Export actions and selectors
export const { clearState } = LoginSlice.actions;

export const loginSelector = (state: { login: LoginState }) => state.login;
