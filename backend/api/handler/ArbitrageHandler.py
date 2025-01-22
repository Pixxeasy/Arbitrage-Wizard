from typing import List

from Demos.win32ts_logoff_disconnected import session
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import select, func, desc
from sqlalchemy.orm import aliased, joinedload, with_loader_criteria

from api.schema.Arbitrage import ArbitrageGroupResponse
from database.model.ArbitrageOpportunity import ArbitrageGroupDBO, ArbitrageOpportunityDBO
from database.model.Exchange import ExchangeDBO
from database.model.User import UserDBO
from database.model.UserConfig import UserConfigDBO
from model.ArbitrageModel import ArbitrageOpportunity
from model import ExchangeInfo


def get_current_arbitrage_by_user_config(user: UserDBO, db: Session, count: int = 3):
    earliest_ts = ExchangeInfo.get_last_total_time(count+1)
    current_time = ExchangeInfo.get_last_total_time(1)
    if not earliest_ts:
        if not current_time:
            current_time = datetime.utcnow().timestamp()
        return [], int(current_time)
    min_count = count

    # Define the ROW_NUMBER() window function
    row_number_column = func.row_number().over(
        partition_by=ArbitrageGroupDBO.trading_pair,  # PARTITION BY name
        order_by=desc(ArbitrageGroupDBO.created_at)  # ORDER BY created_at DESC
    ).label("rn")

    # Define the COUNT() window function
    occurrence_count_column = func.count().over(
        partition_by=ArbitrageGroupDBO.trading_pair  # PARTITION BY name
    ).label("occurrence_count")

    user_config_alias = aliased(UserConfigDBO)
    # Subquery with the window functions
    subquery = (
        select(
            ArbitrageGroupDBO.guid,
            ArbitrageGroupDBO.trading_pair,
            ArbitrageGroupDBO.created_at,
            row_number_column,
            occurrence_count_column,
            user_config_alias.max_amount
        )
        .join(user_config_alias, user_config_alias.exchange_key == ArbitrageGroupDBO.buy_exchange_key)  # Join user_config
        .where(ArbitrageGroupDBO.created_at > earliest_ts,
               user_config_alias.user_id == user.guid)  # Filter by timestamp
        .subquery()
    )

    # Alias the subquery for clarity
    aliased_groups = aliased(ArbitrageGroupDBO, subquery)

    # Main query: Filter for most recent group (rn = 1) and minimum occurrence count
    query = (
        select(ArbitrageGroupDBO)
        .join(subquery, subquery.c.guid == ArbitrageGroupDBO.guid)
        .options(
            joinedload(ArbitrageGroupDBO.opportunities), # Eagerly load opportunities
            with_loader_criteria(
                ArbitrageOpportunityDBO,
                ArbitrageOpportunityDBO.min_usdt_start <= subquery.c.max_amount
            )
        )
        .where(
            subquery.c.rn == 1,  # Only the most recent group per trading_pair
            subquery.c.occurrence_count >= min_count  # Occurrence count > threshold
        )
    )

    arbitrage_dbos: List[ArbitrageGroupDBO] = db.execute(query).unique().scalars().all()
    opportunities = []

    for arbitrage_dbo in arbitrage_dbos:
        if len(arbitrage_dbo.opportunities) == 0:
            continue
        buy_exchange = db.scalars(select(ExchangeDBO).where(ExchangeDBO.config_key == arbitrage_dbo.buy_exchange_key)).first()
        sell_exchange = db.scalars(select(ExchangeDBO).where(ExchangeDBO.config_key == arbitrage_dbo.sell_exchange_key)).first()

        arbitrage_group_response = ArbitrageGroupResponse.model_validate(arbitrage_dbo)
        arbitrage_group_response.buy_exchange_name = buy_exchange.name
        arbitrage_group_response.sell_exchange_name = sell_exchange.name
        opportunities.append(arbitrage_group_response)

    return opportunities, int(current_time)


