from typing import Dict, List, Union
from database.base_db import BaseDB
from models.db import PortfolioDB, PositionDB, OpportunityDB
from DataManager.datamgr.data_extractor import DataExtractor
from utils.tables import PORTFOLIO_TABLE, POSITION_TABLE


class UpdatePort:
    def __init__(self, db: BaseDB):
        self.db = db

    def execute(self) -> None:
        print("Updating portfolio")

        portfolio: PortfolioDB = self.db.read_from_db(PortfolioDB, PORTFOLIO_TABLE)[0]
        portfolio.value = portfolio.buy_power

        positions: List[PositionDB] = self.db.read_from_db(PositionDB, POSITION_TABLE)
        pos_dt: Dict[str, PositionDB] = self.convert_to_ticker_dt(positions)

        prices_dt = self.get_cur_stock_prices(list(pos_dt.keys()))

        for ticker, pos in pos_dt.items():
            cur_price = prices_dt.get(ticker, None)

            for order in pos.orders:
                init_price = order.default_price
                cur_price = init_price if cur_price is None else cur_price
                portfolio.value += order.quantity * cur_price

        self.db.write_to_db([portfolio], PORTFOLIO_TABLE)

    def get_cur_stock_prices(self, tickers: List[str]) -> Dict[str, float]:
        data_extractor = DataExtractor()
        stocks_dt = data_extractor.getListLiveAlpaca(tickers)
        return {ticker: stock["c"] for ticker, stock in stocks_dt.items()}

    def convert_to_ticker_dt(
        self, ll: List[Union[OpportunityDB, PositionDB]]
    ) -> Dict[str, Union[OpportunityDB, PositionDB]]:
        return {x.ticker: x for x in ll}
