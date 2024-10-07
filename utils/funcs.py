from datetime import datetime, timedelta
from typing import Dict, List
from DataManager.datamgr.data_extractor import DataExtractor
from alpaca_trade_api.rest import TimeFrame as AlpacaTimeFrame
from DataManager.utils.timehandler import TimeHandler
from Quantify.tools.portfolio_monitor import PortfolioMonitor
from Quantify.strats.macd_rsi_boll import Macd_Rsi_Boll
from Quantify.constants.timeframe import TimeFrame


from utils.constants import DEFAULT_EXCHANGE, DEFAULT_LOOKBACK


def get_cur_stock_prices(tickers: List[str]) -> Dict[str, float]:
    data_extractor = DataExtractor()
    stocks_dt = data_extractor.getListLiveAlpaca(tickers)
    return {ticker: stock["c"] for ticker, stock in stocks_dt.items()}


def get_stock_price_btwn(ticker: str, list_dates: datetime) -> List[float]:
    data_extractor = DataExtractor()
    stock_dt = data_extractor.getOneHistoricalAlpaca(
        ticker, list_dates[0], list_dates[-2], AlpacaTimeFrame.Day
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


def create_stock_graph(ticker: str) -> None:
    data_extractor = DataExtractor()
    now = datetime.now() - timedelta(days=1)  # Alpaca data is delayed by 1 day
    dt_start = (now - timedelta(days=DEFAULT_LOOKBACK)).strftime("%Y-%m-%d")
    dt_now = now.strftime("%Y-%m-%d")

    stock_dt = data_extractor.getOneHistoricalAlpaca(
        ticker, dt_start, dt_now, AlpacaTimeFrame.Day
    )
    stock_dt.reset_index(inplace=True)
    stock_dt["timestamp"] = stock_dt["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

    dict_df = {ticker: stock_dt}
    strat = Macd_Rsi_Boll(
        sid=1,
        name="macd_rsi_boll",
        timeframe=TimeFrame(100, DEFAULT_LOOKBACK),
        lookback=DEFAULT_LOOKBACK,
    )
    p_mon = PortfolioMonitor(dict_df, strat, DEFAULT_EXCHANGE)
    return p_mon.monitor_health(graph=True, print_debug=False, open_plot=False)
