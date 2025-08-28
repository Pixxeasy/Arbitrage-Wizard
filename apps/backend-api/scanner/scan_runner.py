import asyncio
import datetime as dt
from collections import Counter
from importlib import import_module
from typing import List, Dict

import pandas as pd
from ccxt.base.errors import ExchangeNotAvailable
from dotenv import load_dotenv
from sqlalchemy import update, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from tqdm.asyncio import tqdm as tqdm_async

import scanner.scan_metrics as metrics
from app.database.models.exchange import ExchangeDBO
from app.domain.arbitrage import ArbitrageGroup
from app.domain.exchanges.base_exchange import BaseExchange
from app.domain.orders import OrderBook
from app.domain.trading_pair import Chain
from app.services.arbitrage_service import delete_old_arbitrages
from scanner.util import DEBUG
from scanner.util import run_periodic

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1500)


class ScanRunner:
    def __init__(self, interval: float, session: Session):
        self.task = None
        self.db = session
        self.interval = interval
        self.exchanges: List[BaseExchange] = []
        self.exchangeMap: Dict[str, BaseExchange] = {}
        self.maxAmount = 100

    async def check_arbitrage(self):
        time_start = dt.datetime.now()
        opportunities = []

        delete_old_arbitrages()

        all_pairs = []
        price_task = []
        for ex in self.exchanges:
            price_task.append(ex.load_prices())

            all_pairs.extend(list(ex.trading_pairs.keys()))

        all_pairs = [pair for pair, count in Counter(all_pairs).items() if count > 1]
        await tqdm_async.gather(*price_task, desc="Load prices")

        op_tasks = []
        for pair in all_pairs:
            op_tasks.append(asyncio.create_task(self.find_opportunities(pair)))

        try:
            ops = await tqdm_async.gather(*op_tasks)
            opportunities = [o for op in ops for o in op]
        except Exception:
            return

        time_end = dt.datetime.now()
        total_time = (time_end - time_start).total_seconds()
        if DEBUG:
            if len(opportunities) > 0:
                df = pd.DataFrame([ao.to_dict() for ao in opportunities])
                print(df.sort_values(by=["minProfit"], ascending=False))
            print(f"Took {total_time} seconds")

        metrics.add_time(int(total_time))
        metrics.add_total_time(int(dt.datetime.now(dt.UTC).timestamp()))

    async def start(self, exchange_list):
        await self.load_exchanges(exchange_list)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        await asyncio.create_task(run_periodic(self.interval, self.check_arbitrage))

    async def stop(self):
        for ex in self.exchanges:
            await ex.exchange.close()

        if self.task:
            self.task.cancel()
        self.db.close()

    async def _load_exchange(self, ex_class):
        instance = ex_class()
        get_by_config_key = select(ExchangeDBO).where(ExchangeDBO.config_key == instance.config_key)
        dbo = self.db.scalars(get_by_config_key).first()
        if not dbo:
            dbo = ExchangeDBO(name=instance.name, config_key=instance.config_key)
            self.db.add(dbo)
        else:
            dbo.active = True

        print(f"Load {instance.name} pairs")
        try:
            await instance.load_trading_pairs()
            self.exchanges.append(instance)
            self.exchangeMap[instance.config_key] = instance
            print(f"Finished loading {instance.name} pairs")
        except ExchangeNotAvailable as e:
            print(f"Could not load {instance.name} pairs")
            dbo.active = False
            pass

        self.db.commit()
        instance.guid = dbo.guid

    async def load_exchanges(self, exchange_list):
        # Disable all exchanges
        disable_all_exchanges = update(ExchangeDBO).values(active=False)
        self.db.execute(disable_all_exchanges)
        self.db.commit()

        load_dotenv()
        ex_task = []
        for ex in exchange_list:
            try:
                module = import_module(f"app.domain.exchanges.{ex.lower()}")
                ex_class = getattr(module, ex)
                if issubclass(ex_class, BaseExchange):
                    ex_task.append(self._load_exchange(ex_class))
                else:
                    print(f"Class {ex} is no subclass of BaseExchange")
                    continue
            except Exception as e:
                print(e.with_traceback())
                print(f"No class {ex} was found")

        await tqdm_async.gather(*ex_task, desc="Load exchanges")

        try:
            self.db.commit()
        except IntegrityError:
            pass

    async def find_opportunities(self, pair):

        opportunities = []
        compare_prices = []
        for ex in self.exchanges:
            if pair in list(ex.trading_pairs.keys()):
                compare_prices.append(ex.trading_pairs[pair])

        # Filter all for which no prices have been found
        filtered_pairs = [pair for pair in compare_prices if pair.buy_price and pair.sell_price]

        # No common trading pair in 2 exchanges was found
        if len(filtered_pairs) < 2:
            return opportunities

        # Find best sell und buy price
        sell_prices = sorted(filtered_pairs, key=lambda s: s.sell_price, reverse=True)
        buy_prices = sorted(filtered_pairs, key=lambda s: s.buy_price)

        buy = buy_prices[0]
        sell = sell_prices[0]

        if buy.exchange == sell.exchange:
            return opportunities

        if buy.buy_price * (1 + buy.fee) >= sell.sell_price * (1 - sell.fee):
            return opportunities

        # An estimate profit
        profit = ((sell.sell_price - buy.buy_price) / buy.buy_price) * 100.0

        if profit < 0:
            return opportunities

        # Find matching chain
        for cbName in buy.chains:
            cb: Chain = buy.chains[cbName]
            if not cb.is_allowed_chain():
                continue
            cs: Chain = sell.get_chain(cbName)
            if not cs:
                continue

            if cb.has_contract_address() and cs.has_contract_address():
                if cb.contract_address != cs.contract_address:
                    continue

            # Withdraw on buy side and deposit on sell side are possible
            if cb.withdraw and cs.deposit:

                # Calculate minimum amount of profit
                min_amount = self.calculate_min_profit_amount(buy.buy_price, sell.sell_price, cb.fee, buy.fee, sell.fee,
                                                              1)
                if max(min_amount, cb.fee * buy.buy_price) > self.maxAmount:
                    continue

                buy_exchange = self.exchangeMap[buy.exchange]
                sell_exchange = self.exchangeMap[sell.exchange]

                # Get orderbook of coin on buy exchange

                buy_orders: OrderBook = await buy_exchange.get_orders(buy.symbol)

                if not buy_orders:
                    continue

                # Get all possibilities for buying

                buy_possibilities = buy_orders.get_buy_possibilities(max(min_amount, cb.fee),
                                                                     cb.fee, sell.sell_price, sell.fee, self.maxAmount)
                if len(buy_possibilities) == 0:
                    continue

                # Get orderbook of coin on sell exchange
                sell_orders: OrderBook = await sell_exchange.get_orders(sell.symbol)

                if not sell_orders:
                    continue

                sell_ops = sell_orders.get_sell_opportunities(buy_possibilities, 1.0)

                if len(sell_ops) == 0:
                    continue

                ag = ArbitrageGroup(buy_exchange_name=buy_exchange.name, sell_exchange_name=sell_exchange.name,
                                    trading_pair=pair,
                                    chain=cb.name, buy_exchange_key=buy_exchange.config_key,
                                    sell_exchange_key=sell_exchange.config_key)
                ag.set_opportunities(sell_ops)
                opportunities.append(ag)
                self.db.add(ag.to_DBO())
                self.db.commit()

        return opportunities

    def calculate_min_profit_amount(self, buy_price, sell_price, withdraw_fee, buy_fee, sell_fee, profit):
        first = withdraw_fee * sell_price * (1 - sell_fee)
        second = (1 - buy_fee) * sell_price * (1 - sell_fee) / buy_price - (1 + (profit / 100))

        return first / second
