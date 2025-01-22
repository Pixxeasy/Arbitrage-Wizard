from typing import List

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.model.BaseModel import Base, TimestampMixin, BaseDBO


class ArbitrageOpportunityDBO(BaseDBO, TimestampMixin):
    __tablename__ = 'arbitrage_opportunities'

    min_usdt_start: Mapped[float]
    min_usdt_end: Mapped[float]
    max_usdt_start: Mapped[float]
    max_usdt_end: Mapped[float]
    min_profit: Mapped[float]
    max_profit: Mapped[float]
    buy_price: Mapped[float]
    sell_price: Mapped[float]

    group_id: Mapped[str] = mapped_column(ForeignKey('arbitrage_groups.guid'))




class ArbitrageGroupDBO(BaseDBO, TimestampMixin):
    __tablename__ = 'arbitrage_groups'

    buy_exchange_key: Mapped[str] = mapped_column(ForeignKey('exchanges.config_key'))
    sell_exchange_key: Mapped[str] = mapped_column(ForeignKey('exchanges.config_key'))
    trading_pair: Mapped[str]
    chain: Mapped[str]
    opportunities: Mapped[List["ArbitrageOpportunityDBO"]] = relationship()


