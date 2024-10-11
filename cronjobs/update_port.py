from typing import Dict, List, Union

from sqlmodel import select, update
from database.sql_db import SqlDB
from models.db import HistoryDB, PortfolioDB, PositionDB, OpportunityDB
from utils.funcs import get_cur_stock_prices
from utils.tables import PORTFOLIO_TABLE, POSITION_TABLE
from datetime import datetime


class UpdatePort:
    def __init__(self, db: SqlDB):
        self.db = db

    def execute(self) -> None:

        print("Updating portfolio")
        session = next(self.db.get_session())
        # TODO: backfill portfolio values from start if any are missing

        portfolios: List[PortfolioDB] = session.exec(select(PortfolioDB)).all()

        for portfolio in portfolios:
            portfolio.history = [HistoryDB(**hist) for hist in portfolio.history]
            portfolio.value = portfolio.buy_power

            positions: List[PositionDB] = session.exec(
                select(PositionDB).where(
                    PositionDB.email_address == portfolio.email_address
                )
            ).all()

            if not positions:
                print("No positions to update")
                return

            pos_dt: Dict[str, PositionDB] = self.convert_to_ticker_dt(positions)

            prices_dt = get_cur_stock_prices(list(pos_dt.keys()))

            for ticker, pos in pos_dt.items():
                cur_price = prices_dt.get(ticker, None)

                for order in pos.orders:
                    init_price = order.default_price
                    cur_price = init_price if cur_price is None else cur_price
                    portfolio.value += order.quantity * cur_price

            last_hist = portfolio.history[-1] if portfolio.history else None
            last_hist_entry = HistoryDB(
                timestamp=self.get_cur_date(), value=portfolio.value
            )

            if last_hist is None or last_hist.timestamp != self.get_cur_date():
                portfolio.history.append(last_hist_entry)
            else:
                portfolio.history[-1] = last_hist_entry

            session.exec(
                update(PortfolioDB)
                .where(PortfolioDB.email_address == portfolio.email_address)
                .values(portfolio)
            )

    def convert_to_ticker_dt(
        self, ll: List[Union[OpportunityDB, PositionDB]]
    ) -> Dict[str, Union[OpportunityDB, PositionDB]]:
        return {x.ticker: x for x in ll}

    def get_cur_date(self):
        return datetime.now().strftime("%Y-%m-%d")
