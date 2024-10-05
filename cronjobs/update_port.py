from typing import Dict, List, Union
from database.base_db import BaseDB
from models.db import PortfolioDB, PositionDB, OpportunityDB
from utils.funcs import get_cur_stock_prices
from utils.tables import PORTFOLIO_TABLE, POSITION_TABLE
from datetime import datetime


class UpdatePort:
    def __init__(self, db: BaseDB):
        self.db = db

    def execute(self) -> None:

        print("Updating portfolio")

        portfolio: PortfolioDB = self.db.read_from_db(PortfolioDB, PORTFOLIO_TABLE)[0]

        portfolio.value = portfolio.buy_power

        positions: List[PositionDB] = self.db.read_from_db(PositionDB, POSITION_TABLE)

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
        if last_hist is None or last_hist[0] != self.get_cur_date():
            portfolio.history.append((self.get_cur_date(), portfolio.value))
        else:
            portfolio.history[-1] = (self.get_cur_date(), portfolio.value)

        self.db.write_to_db([portfolio], PORTFOLIO_TABLE)

    def convert_to_ticker_dt(
        self, ll: List[Union[OpportunityDB, PositionDB]]
    ) -> Dict[str, Union[OpportunityDB, PositionDB]]:
        return {x.ticker: x for x in ll}

    def get_cur_date(self):
        return datetime.now().strftime("%Y-%m-%d")
