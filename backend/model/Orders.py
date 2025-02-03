from typing import List, Self

from pydantic import BaseModel, Field

from model.ArbitrageModel import ArbitrageOpportunity, Possibility


class Order(BaseModel):

    price: float = Field(gt=0)
    quantity: float = Field(gt=0)
    usdt_amount: float = Field(gt=0, default_factory=lambda cls: (cls["price"]*cls["quantity"]))

class OrderResult(BaseModel):
    usdt_amount: float = Field(gt=0)
    coin_amount: float = Field(gt=0)
    rate: float = Field(gt=0)

    def include_withdraw_fee(self, withdraw_fee: float) -> Self:
        self.coin_amount -= withdraw_fee
        self.rate = self.usdt_amount / self.coin_amount

        return self

class OrderBook(BaseModel):

    buy_orders: List[Order] = Field(default=[])
    sell_orders: List[Order] = Field(default=[])
    buy_fee: float = Field(ge=0)
    sell_fee: float = Field(ge=0)

    def get_total_buy_price(self,usdt_amount: float) -> OrderResult:
        amount_left = usdt_amount
        total_price = 0

        for i, o in enumerate(self.buy_orders):
            if amount_left <= o.usdt_amount:
                total_price += (amount_left / o.price) * (1 - self.buy_fee)
                return OrderResult(usdt_amount=usdt_amount, coin_amount=total_price, rate=usdt_amount/total_price)
            else:
                total_price += o.quantity * (1 - self.buy_fee)
                amount_left -= o.usdt_amount

        return OrderResult(usdt_amount=usdt_amount, coin_amount=total_price, rate=usdt_amount / total_price)

    def get_total_sell_price(self,coin_amount: float) -> OrderResult:
        amount_left = coin_amount
        total_price = 0

        for i, o in enumerate(self.sell_orders):
            if amount_left <= o.quantity:
                total_price += amount_left * o.price * (1 - self.sell_fee)
                return OrderResult(usdt_amount=total_price, coin_amount=coin_amount, rate=total_price/coin_amount)
            else:
                total_price += o.usdt_amount * (1 - self.sell_fee)
                amount_left -= o.quantity

        return OrderResult(usdt_amount=total_price, coin_amount=coin_amount, rate=total_price / coin_amount)

    def get_buy_possibilities(self, usdt_amount: float, withdraw_fee:float, sell_price:float, sell_fee:float, max_amount:float) -> List[Possibility]:
        possibilities = []
        if len(self.sell_orders) == 0:
            return possibilities

        buy_price = self.buy_orders[0].price
        sell_price_with_fee = sell_price * (1 - sell_fee)
        min_amount = usdt_amount
        current_amount = 0

        # Buyprice already too high
        if buy_price * (1 + self.buy_fee) >= sell_price_with_fee:
            return possibilities

        for i, order in enumerate(self.buy_orders):
            current_amount += order.usdt_amount
            current_amount = min(current_amount, max_amount)
            max_result = self.get_total_buy_price(current_amount).include_withdraw_fee(withdraw_fee)

            if max_result.rate > sell_price_with_fee:
                continue

            remove_amount = self._calculate_min_buy_amount(sell_price_with_fee, withdraw_fee, order.price,
                                                           current_amount, i)

            if (remove_amount < 0) or (current_amount - remove_amount < min_amount):
                continue

            min_buy_amount = current_amount - remove_amount

            min_result = self.get_total_buy_price(min_buy_amount).include_withdraw_fee(withdraw_fee)
            if ((min_result.rate) < 0 or (min_result.coin_amount) < 0):
                continue

            if (min_result.rate > sell_price_with_fee):
                continue

            pos = Possibility(min_usdt_amount=min_buy_amount, max_usdt_amount=current_amount,rate=min_result.rate,
                              min_coin_amount=min_result.coin_amount, max_coin_amount=max_result.coin_amount)

            possibilities.append(pos)

            if current_amount == max_amount:
                return possibilities

        return possibilities

    def get_sell_opportunities(self, buy_possibilities: List[Possibility], profit_percent: float) -> List[ArbitrageOpportunity ]:
        opportunities = []
        if len(self.sell_orders) == 0:
            return opportunities

        for pos in buy_possibilities:
            min_result = self.get_total_sell_price(pos.min_coin_amount)
            max_result = self.get_total_sell_price(pos.max_coin_amount)

            min_profit = min_result.usdt_amount - pos.min_usdt_amount
            max_profit = max_result.usdt_amount - pos.max_usdt_amount

            if (min_profit > pos.min_usdt_amount * (profit_percent / 100)) and (
                    max_profit > pos.max_usdt_amount * (profit_percent / 100)):

                ao = ArbitrageOpportunity(min_usdt_start=pos.min_usdt_amount, max_usdt_start=pos.max_usdt_amount,
                                          min_usdt_end=min_result.usdt_amount, max_usdt_end=max_result.usdt_amount,
                                          min_profit=min_profit, max_profit=max_profit, buy_price=pos.rate,
                                          sell_price=min_result.rate)


                opportunities.append(ao)

        return opportunities

    def _calculate_min_buy_amount(self, sell_price, withdraw_fee, buy_price, amount, level ):

        total_price = sum(self.buy_orders[i].quantity for i in range(level+1))
        numerator = sell_price * total_price * (1-self.buy_fee) - amount - sell_price * withdraw_fee
        denominator = (1+ (sell_price*(1-buy_price)/buy_price))

        return numerator/denominator

