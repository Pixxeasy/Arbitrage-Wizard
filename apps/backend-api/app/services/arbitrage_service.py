import datetime as dt
from typing import List

from sqlalchemy import select, func, desc, case, literal_column, delete
from sqlalchemy.orm import Session
from sqlalchemy.orm import aliased, joinedload, with_loader_criteria

from app.database.models.arbitrage_opportunity import ArbitrageGroupDBO, ArbitrageOpportunityDBO
from app.database.models.exchange import ExchangeDBO
from app.database.models.user import UserDBO
from app.database.models.user_config import UserConfigDBO
from app.schemas.arbitrage import ArbitrageGroupResponse, HistoricArbitrage
from scanner.scan_metrics import get_last_total_time, get_relaxed_time


def get_current_arbitrage_by_user_config(user: UserDBO, db: Session, count: int = 3):
    earliest_ts = get_last_total_time(count + 1)
    current_time = get_last_total_time(1)
    if not earliest_ts:
        if not current_time:
            current_time = dt.datetime.now(dt.UTC).timestamp()
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
        .join(user_config_alias,
              user_config_alias.exchange_key == ArbitrageGroupDBO.buy_exchange_key)  # Join user_config
        .where(ArbitrageGroupDBO.created_at > earliest_ts,
               user_config_alias.user_id == user.guid)  # Filter by timestamp
        .subquery()
    )

    # Main query: Filter for most recent group (rn = 1) and minimum occurrence count
    query = (
        select(ArbitrageGroupDBO)
        .join(subquery, subquery.c.guid == ArbitrageGroupDBO.guid)
        .options(
            joinedload(ArbitrageGroupDBO.opportunities),  # Eagerly load opportunities
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
        buy_exchange = db.scalars(
            select(ExchangeDBO).where(ExchangeDBO.config_key == arbitrage_dbo.buy_exchange_key)).first()
        sell_exchange = db.scalars(
            select(ExchangeDBO).where(ExchangeDBO.config_key == arbitrage_dbo.sell_exchange_key)).first()

        arbitrage_group_response = ArbitrageGroupResponse.model_validate(arbitrage_dbo)
        arbitrage_group_response.buy_exchange_name = buy_exchange.name
        arbitrage_group_response.sell_exchange_name = sell_exchange.name
        opportunities.append(arbitrage_group_response)

    return opportunities, int(current_time)


def get_historic_arbitrages(db: Session, limit: int = 100):
    split_time = 3 * get_relaxed_time()
    history = []
    time_diff_cte = (
        select(
            ArbitrageGroupDBO.guid,
            ArbitrageGroupDBO.created_at,
            ArbitrageGroupDBO.sell_exchange_key,
            ArbitrageGroupDBO.buy_exchange_key,
            ArbitrageGroupDBO.trading_pair,
            (ArbitrageGroupDBO.created_at - func.lag(ArbitrageGroupDBO.created_at)
             .over(partition_by=ArbitrageGroupDBO.trading_pair, order_by=ArbitrageGroupDBO.created_at)).label(
                'time_diff')
        )
        .cte("TimeDiff")
    )

    # Step 2: Define the Series CTE
    series_cte = (
        select(
            time_diff_cte.c.guid,
            time_diff_cte.c.created_at,
            time_diff_cte.c.sell_exchange_key,
            time_diff_cte.c.buy_exchange_key,
            time_diff_cte.c.trading_pair,
            func.sum(
                case(
                    (time_diff_cte.c.time_diff > literal_column(str(split_time)), 1),
                    else_=0
                )
            )
            .over(partition_by=time_diff_cte.c.trading_pair, order_by=time_diff_cte.c.created_at)
            .label('series_id')
        )
        .cte("Series")
    )

    # Step 3: Final query
    query = (
        select(
            series_cte.c.series_id,
            series_cte.c.trading_pair,
            func.min(series_cte.c.created_at).label('series_start'),
            func.max(series_cte.c.created_at).label('series_end'),
            func.count().label('num_runs'),
            series_cte.c.sell_exchange_key,
            series_cte.c.buy_exchange_key
        )
        .group_by(series_cte.c.series_id, series_cte.c.trading_pair, series_cte.c.sell_exchange_key)
        .having(func.count() > 1)
        .order_by(func.min(series_cte.c.created_at))
        .limit(limit)
    )

    results = db.execute(query).fetchall()
    arbitrage_dbos: List[HistoricArbitrage] = [
        HistoricArbitrage(
            trading_pair=row.trading_pair,
            series_start=int(row.series_start),
            series_end=int(row.series_end),
            num_runs=row.num_runs,
            sell_exchange_key=row.sell_exchange_key,
            buy_exchange_key=row.buy_exchange_key
        )
        for row in results
    ]
    for arbitrage_dbo in arbitrage_dbos:
        buy_exchange = db.scalars(
            select(ExchangeDBO).where(ExchangeDBO.config_key == arbitrage_dbo.buy_exchange_key)).first()
        sell_exchange = db.scalars(
            select(ExchangeDBO).where(ExchangeDBO.config_key == arbitrage_dbo.sell_exchange_key)).first()

        arbitrage_dbo.buy_exchange_name = buy_exchange.name
        arbitrage_dbo.sell_exchange_name = sell_exchange.name
        history.append(arbitrage_dbo)

    return history


def delete_old_arbitrages(db: Session):
    lower_limit = int((dt.datetime.now(dt.UTC) - dt.timedelta(days=1)).timestamp())

    stmt = delete(ArbitrageGroupDBO).where(ArbitrageGroupDBO.created_at <= lower_limit)

    db.execute(stmt)
    db.commit()
