from datetime import datetime
from typing import Dict, List
from DataManager.datamgr.data_extractor import DataExtractor
from alpaca_trade_api.rest import TimeFrame
from DataManager.utils.timehandler import TimeHandler


def get_cur_stock_prices(tickers: List[str]) -> Dict[str, float]:
    data_extractor = DataExtractor()
    stocks_dt = data_extractor.getListLiveAlpaca(tickers)
    return {ticker: stock["c"] for ticker, stock in stocks_dt.items()}


def get_stock_price_btwn(ticker: str, list_dates: datetime) -> List[float]:
    data_extractor = DataExtractor()
    stock_dt = data_extractor.getOneHistoricalAlpaca(
        ticker, list_dates[0], list_dates[-2], TimeFrame.Day
    )
    dt = stock_dt["close"].tolist()

    mn_dt = TimeHandler.get_datetime_from_timestamp(min(stock_dt.index)).replace(
        minute=0, hour=0, second=0, microsecond=0
    )
    mx_dt = TimeHandler.get_datetime_from_timestamp(max(stock_dt.index)).replace(
        minute=0, hour=0, second=0, microsecond=0
    )
    mn_req = TimeHandler.get_datetime_from_alpaca_string(list_dates[0])
    mx_req = TimeHandler.get_datetime_from_alpaca_string(list_dates[-1])

    # pad the start and end of the list with the first and last values
    if mn_dt > mn_req:
        dt = ([dt[0]] * (mn_dt - mn_req).days) + dt
    if mx_dt < mx_req:
        dt = dt + [dt[-1]] * ((mx_req - mx_dt).days)

    return dt
