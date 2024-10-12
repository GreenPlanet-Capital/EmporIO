from typing import Dict, List, Tuple, Union
from DataManager.datamgr.data_manager import DataManager
from DataManager.utils.timehandler import TimeHandler
from datetime import datetime

import pandas as pd


class DataMgrIntegrator:
    def __init__(
        self, exchange_name: str, limit: Union[int, None], update_tickers: bool
    ) -> None:
        self.exchange_name = exchange_name
        self.datamgr = DataManager(
            exchangeName=exchange_name, limit=limit, update_before=update_tickers
        )

    def get_data(
        self, start_timestamp: datetime, end_timestamp: datetime
    ) -> Tuple[List[str], Dict[str, pd.DataFrame]]:
        start_dt, end_dt = map(
            TimeHandler.get_string_from_datetime, [start_timestamp, end_timestamp]
        )
        dict_of_dfs = self.datamgr.get_stock_data(
            start_dt, end_dt, api="Alpaca", fetch_data=True
        )
        return self.datamgr.list_of_symbols, dict_of_dfs
