from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import select, func

from database.model.ArbitrageOpportunity import ArbitrageGroupDBO


def get_current_arbitrage_by_user_config(user_config, db: Session, time_period: int = 5):
    max_amount = user_config['max_amount']
    earliest_ts = (datetime.now() - timedelta(minutes=time_period)).timestamp()
    min_count = int((time_period*60)/40)

    select_by_timestamp = (select(ArbitrageGroupDBO)
                           .join(ArbitrageGroupDBO.opportunities)
                           .where(ArbitrageGroupDBO.created_at >= earliest_ts)
                           .group_by(ArbitrageGroupDBO.trading_pair)
                           .having(func.count(ArbitrageGroupDBO.trading_pair) >= min_count))

    arbitrage_dbos = db.scalars(select_by_timestamp).all()


