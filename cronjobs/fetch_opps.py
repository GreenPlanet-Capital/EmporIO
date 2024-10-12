from typing import Tuple

import pytz
from sqlmodel import delete
from database.sql_db import SqlDB
from integration.datamgr import DataMgrIntegrator
from integration.quantify import QuantifyIntegrator
from datetime import datetime, timedelta
from Quantify.positions.opportunity import Opportunity
from models.db import OpportunityDB
from utils.constants import DEFAULT_EXCHANGE, DEFAULT_LOOKBACK
from DataManager.utils.timehandler import TimeHandler
import pandas_market_calendars as mcal
import pandas as pd


class FetchOpps:
    def __init__(self, db: SqlDB):
        self.db = db

    def execute(self) -> None:
        print("Fetching opportunities")

        data_mgr = DataMgrIntegrator(
            exchange_name=DEFAULT_EXCHANGE, limit=None, update_tickers=False
        )

        start_timestamp, end_timestamp = self.get_dates()
        symbols, dict_stock_df = data_mgr.get_data(start_timestamp, end_timestamp)

        quant_integrator = QuantifyIntegrator(
            symbols=symbols,
            dict_stock_df=dict_stock_df,
            exchange_name=DEFAULT_EXCHANGE,
            num_recommendations=1e9,
            percent_long=1,  # RH doesn't support shorting
        )

        opps = quant_integrator.get_positions()
        opps_db = [self.opp_to_db(opp) for opp in opps]

        print("Opportunities fetched")

        session = next(self.db.get_session())
        session.exec(delete(OpportunityDB))
        session.add_all(opps_db)
        session.commit()

        print("Opportunities saved")

    def get_dates(self) -> Tuple[datetime, datetime]:
        cal = mcal.get_calendar(DEFAULT_EXCHANGE)
        today = datetime.now(tz=pytz.timezone("US/Eastern")).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        start_timestamp = today - pd.tseries.offsets.CustomBusinessDay(
            n=DEFAULT_LOOKBACK + 10, calendar=cal  # Some buffer
        )
        end_timestamp = today - timedelta(days=1)  # Alpaca data is delayed by 1 day

        return start_timestamp, end_timestamp

    def opp_to_db(self, opp: Opportunity) -> OpportunityDB:
        return OpportunityDB(
            strategy_id=opp.strategy_id,
            ticker=opp.ticker,
            exchangeName=opp.exchangeName,
            timestamp=TimeHandler.get_alpaca_string_from_datetime(opp.timestamp),
            order_type=opp.order_type,
            default_price=opp.default_price,
            metadata_score=opp.metadata["score"],
        )
