from typing import List

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.model.BaseModel import Base, TimestampMixin, BaseDBO


class ArbitrageOpportunityDBO(BaseDBO, TimestampMixin):
    __tablename__ = 'arbitrage_opportunities'

    min_usdt_start: Mapped[float] = mapped_column()
    min_usdt_end: Mapped[float] = mapped_column()
    max_usdt_start: Mapped[float] = mapped_column()
    max_usdt_end: Mapped[float] = mapped_column()
    min_profit: Mapped[float] = mapped_column()
    max_profit: Mapped[float] = mapped_column()
    buy_price: Mapped[float] = mapped_column()
    sell_price: Mapped[float] = mapped_column()

    group_id: Mapped[str] = mapped_column(ForeignKey('arbitrage_groups.guid'))




class ArbitrageGroupDBO(BaseDBO, TimestampMixin):
    __tablename__ = 'arbitrage_groups'

    buy_exchange_id: Mapped[str] = mapped_column(ForeignKey('exchanges.guid'))
    sell_exchange_id: Mapped[str] = mapped_column(ForeignKey('exchanges.guid'))
    trading_pair: Mapped[str] = mapped_column()
    chain: Mapped[str] = mapped_column()
    opportunities: Mapped[List["ArbitrageOpportunityDBO"]] = relationship()


