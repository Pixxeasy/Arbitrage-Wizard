import asyncio
from typing import Optional

from ccxt import RequestTimeout

from app.domain.exchanges.base_exchange import BaseExchange

chains = {
    "BSC_BNB": "BEP20",
    "POLYGON": "MATIC",
    "DOGECHAIN": "DOGE",
    "LAIKA-DOGE": "DOGE",
    "AVAX-C": "AVAX",
    "LIGHTNING_BTC": "LIGHTNING",
    "ARBI": "ARBITRUM",
    "ZKSYNCERA_ETH": "zkSync",
    "ETH": "ERC20",
    "TRX": "TRC20"
}


class BitMart(BaseExchange):
    name: Optional[str] = "BitMart"
    ccxt_id: Optional[str] = "bitmart"
    config_key: Optional[str] = "btm"

    async def load_trading_pairs(self):
        currencies = await self.fetch_currencies()

        await self.load_trading_pairs_base(contract_address=["contract_address"], currencies=currencies)

    async def fetch_currencies(self):

        try:
            currencies = await self.exchange.fetch("https://api-cloud.bitmart.com/account/v1/currencies")
        except RequestTimeout:
            asyncio.sleep(1)
            currencies = await self.exchange.fetch("https://api-cloud.bitmart.com/account/v1/currencies")

        currency_list = {}

        for cur in currencies["data"]["currencies"]:
            network = cur["network"]
            name = cur["currency"]
            if "-" in name:
                name_split = name.split("-")
                if len(name_split[1]) > 2:
                    name = name_split[1]

            if cur["contract_address"]:

                if network in chains.keys():
                    network = chains[network]

            if network in chains.keys():
                network = chains[network]

            if name not in currency_list.keys():
                currency_list[name] = {}

            currency_list[name][network] = {
                "contract_address": cur["contract_address"],
                "fee": cur["withdraw_minfee"],
                "min_amount": cur["withdraw_minsize"],
                "withdraw": cur["withdraw_enabled"],
                "deposit": cur["deposit_enabled"]
            }

        return currency_list
