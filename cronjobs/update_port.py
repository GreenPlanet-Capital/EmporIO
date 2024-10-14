from typing import Dict, List, Union

from fastapi.encoders import jsonable_encoder
import pytz
from sqlmodel import select, update
from database.sql_db import SqlDB
from models.db import HistoryDB, OrderDB, PortfolioDB, PositionDB, OpportunityDB
from utils.funcs import get_cur_stock_prices
from DataManager.utils.timehandler import TimeHandler
from datetime import datetime, timedelta


class UpdatePort:
    def __init__(self, db: SqlDB):
        self.db = db

    def execute(self) -> None:

        print("Updating portfolio")
        session = next(self.db.get_session())

        portfolios: List[PortfolioDB] = session.exec(select(PortfolioDB)).all()

        for portfolio in portfolios:
            portfolio.value = portfolio.buy_power

            positions: List[PositionDB] = session.exec(
                select(PositionDB).where(
                    PositionDB.email_address == portfolio.email_address
                )
            ).all()

            if not positions:
                print("No positions to update")
                return

            portfolio.history = [HistoryDB(**hist) for hist in portfolio.history]
            pos_dt: Dict[str, PositionDB] = self.convert_to_ticker_dt(positions)

            prices_dt = get_cur_stock_prices(list(pos_dt.keys()))

            for ticker, pos in pos_dt.items():
                cur_price = prices_dt.get(ticker, None)

                for order in pos.orders:
                    init_price = order["default_price"]
                    cur_price = init_price if cur_price is None else cur_price
                    portfolio.value += order["quantity"] * cur_price

            last_hist = portfolio.history[-1] if portfolio.history else None
            cur_dt_alp = self.get_cur_date()
            last_hist_entry = HistoryDB(timestamp=cur_dt_alp, value=portfolio.value)

            if last_hist is None or last_hist.timestamp != cur_dt_alp:
                portfolio.history.append(last_hist_entry)
            else:
                portfolio.history[-1] = last_hist_entry

            # backfill portfolio values from start if any are missing
            start_dt = TimeHandler.get_datetime_from_alpaca_string(
                portfolio.history[0].timestamp
            )
            cur_dt = TimeHandler.get_datetime_from_alpaca_string(cur_dt_alp)
            map_dt = {hist.timestamp: hist.value for hist in portfolio.history}
            lst_exists = portfolio.history[0].value

            for i in range((cur_dt - start_dt).days):
                hist_dt = start_dt + timedelta(days=i)
                hist_dt_alp = TimeHandler.get_alpaca_string_from_datetime(hist_dt)
                if hist_dt_alp not in map_dt:
                    # take neighboring values
                    portfolio.history.append(
                        HistoryDB(timestamp=hist_dt_alp, value=lst_exists)
                    )
                else:
                    lst_exists = map_dt[hist_dt_alp]

            portfolio.history = sorted(
                portfolio.history,
                key=lambda x: TimeHandler.get_datetime_from_alpaca_string(x.timestamp),
            )
            portfolio.history = [jsonable_encoder(hist) for hist in portfolio.history]

            session.exec(
                update(PortfolioDB)
                .where(PortfolioDB.email_address == portfolio.email_address)
                .values(
                    buy_power=portfolio.buy_power,
                    value=portfolio.value,
                    history=portfolio.history,
                )
            )
            session.commit()

    def convert_to_ticker_dt(
        self, ll: List[Union[OpportunityDB, PositionDB]]
    ) -> Dict[str, Union[OpportunityDB, PositionDB]]:
        return {l.ticker: l for l in ll}

    def get_cur_date(self):
        return datetime.now(tz=pytz.timezone("US/Eastern")).strftime("%Y-%m-%d")
