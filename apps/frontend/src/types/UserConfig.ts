export interface UserConfig {
    maxAmount: number;
    exchangeShort: string;
    exchangeLong: string;
    apiKey?: string;
    apiSecret?: string;
    apiPassphrase?: string;
}

export interface ConfigResponse {
    max_amount: number;
    exchange_key: string;
    api_key?: string;
    api_secret?: string;
    api_passphrase?: string;
}

export interface ExchangeResponse {
    config_key: string;
    name: string
}