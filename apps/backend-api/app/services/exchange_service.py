from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.exchange import ExchangeDBO
from app.database.models.user import UserDBO
from app.database.models.user_config import UserConfigDBO
from app.schemas.exchange import SimpleExchange
from app.schemas.user import UserConfig


def get_available_exchanges(db: Session) -> List[SimpleExchange]:
    exchanges = []

    stmt_avail_exchanges = select(ExchangeDBO).where(ExchangeDBO.active)

    dbos = db.scalars(stmt_avail_exchanges).all()
    for dbo in dbos:
        exchanges.append(SimpleExchange.model_validate(dbo))

    return exchanges


def get_user_configs(db: Session, user: UserDBO) -> List[UserConfig]:
    user_configs = []

    for dbo in user.configs:
        user_configs.append(UserConfig.model_validate(dbo))

    return user_configs


def add_user_configs(db: Session, configs: List[UserConfig], user: UserDBO) -> List[UserConfig]:
    user_exchange_names = [c.exchange_key for c in user.configs]
    user_configs = []

    for config in configs:
        if config.exchange_key in user_exchange_names:
            continue
        user_config_dbo = UserConfigDBO(max_amount=config.max_amount, exchange_key=config.exchange_key,
                                        user_id=user.guid, api_key=config.api_key, api_secret=config.api_secret,
                                        api_passphrase=config.api_passphrase)
        db.add(user_config_dbo)
        user_configs.append(config)

    db.commit()

    return user_configs


def edit_user_configs(db: Session, configs: List[UserConfig], user: UserDBO) -> List[UserConfig]:
    user_configs = []

    for config in configs:
        stmt = (select(UserConfigDBO)
                .where(UserConfigDBO.user_id == user.guid,
                       UserConfigDBO.exchange_key == config.exchange_key))
        user_config_dbo = db.scalars(stmt).first()
        if not user_config_dbo:
            user_config_dbo = UserConfigDBO(max_amount=config.max_amount, exchange_key=config.exchange_key,
                                            user_id=user.guid, api_key=config.api_key, api_secret=config.api_secret,
                                            api_passphrase=config.api_passphrase)
            db.add(user_config_dbo)
        else:
            user_config_dbo.max_amount = config.max_amount
            user_config_dbo.api_key = config.api_key
            user_config_dbo.api_secret = config.api_secret
            user_config_dbo.api_passphrase = config.api_passphrase

        user_configs.append(config)

    db.commit()

    return user_configs
