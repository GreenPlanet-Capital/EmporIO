from typing import Dict, List
from DataManager.datamgr.data_extractor import DataExtractor


def get_cur_stock_prices(tickers: List[str]) -> Dict[str, float]:
    data_extractor = DataExtractor()
    stocks_dt = data_extractor.getListLiveAlpaca(tickers)
    return {ticker: stock["c"] for ticker, stock in stocks_dt.items()}
