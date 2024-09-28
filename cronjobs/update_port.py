from typing import Dict, List, Union
from database.base_db import BaseDB
from models.db import PortfolioDB, PositionDB, OpportunityDB
from utils.tables import OPPORTUNITY_TABLE, PORTFOLIO_TABLE, POSITION_TABLE


class UpdatePort:
    def __init__(self, db: BaseDB):
        self.db = db

    def execute(self) -> None:
        print("Updating portfolio")

        portfolio: PortfolioDB = self.db.read_from_db(PortfolioDB, PORTFOLIO_TABLE)[0]
        portfolio.value = portfolio.buy_power

        positions: List[PositionDB] = self.db.read_from_db(PositionDB, POSITION_TABLE)
        pos_dt: Dict[str, PositionDB] = self.convert_to_ticker_dt(positions)

        opportunities: List[OpportunityDB] = self.db.read_from_db(
            OpportunityDB, OPPORTUNITY_TABLE
        )
        opp_dt: Dict[str, OpportunityDB] = self.convert_to_ticker_dt(opportunities)

        for ticker, pos in pos_dt.items():
            opp = opp_dt.get(ticker, None)

            for order in pos.orders:
                init_price = order.default_price
                cur_price = init_price if opp is None else opp.default_price
                portfolio.value += order.quantity * cur_price

        self.db.write_to_db([portfolio], PORTFOLIO_TABLE)

    def convert_to_ticker_dt(
        self, ll: List[Union[OpportunityDB, PositionDB]]
    ) -> Dict[str, Union[OpportunityDB, PositionDB]]:
        return {x.ticker: x for x in ll}
