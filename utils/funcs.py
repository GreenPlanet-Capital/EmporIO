from datetime import datetime, timedelta
from typing import Dict, List
from plotly.graph_objs import Figure
import pandas as pd
import pytz
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


def get_stock_price_btwn(ticker: str, list_dates: List[str]) -> List[float]:
    if len(list_dates) < 2:
        raise ValueError("Need at least 2 dates to interpolate")

    data_extractor = DataExtractor()
    stock_dt = data_extractor.getOneHistoricalAlpaca(
        ticker, list_dates[0], list_dates[-2], AlpacaTimeFrame.Day
    )
    stock_dt.reset_index(inplace=True)
    stock_dt["timestamp_str"] = stock_dt["timestamp"].apply(
        TimeHandler.get_alpaca_string_from_timestamp
    )
    stock_dt["timestamp"] = stock_dt["timestamp_str"].apply(
        TimeHandler.get_datetime_from_alpaca_string
    )
    existing_dt = set(stock_dt["timestamp_str"].tolist())

    # pad the missing days with neighboring values
    for pos_dt in list_dates:
        if pos_dt not in existing_dt:
            stock_dt = add_dummy_row(stock_dt, pos_dt)

    stock_dt = stock_dt.sort_values(by="timestamp")
    dt = stock_dt["close"].tolist()
    return dt


def add_dummy_row(stock_dt: pd.DataFrame, pos_dt: str) -> pd.DataFrame:
    pos_dt_parsed = TimeHandler.get_datetime_from_alpaca_string(pos_dt)
    before_stock_dt = stock_dt[stock_dt["timestamp"] < pos_dt_parsed]
    after_stock_dt = stock_dt[stock_dt["timestamp"] > pos_dt_parsed]

    if not before_stock_dt.empty:
        rep_stock_sr = before_stock_dt.iloc[-1]
    elif not after_stock_dt.empty:
        rep_stock_sr = after_stock_dt.iloc[0]
    else:
        raise ValueError("No data to interpolate")

    rep_stock_sr["timestamp"] = pos_dt_parsed
    rep_stock_sr["timestamp_str"] = pos_dt
    stock_dt = pd.concat([stock_dt, pd.DataFrame(rep_stock_sr).T])

    return stock_dt


def create_stock_graph(ticker: str, order_type: int) -> Figure:
    data_extractor = DataExtractor()
    now = datetime.now(tz=pytz.timezone("US/Eastern")) - timedelta(
        days=1
    )  # Alpaca data is delayed by 1 day
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
    return p_mon.monitor_health(
        graph=True, print_debug=False, open_plot=False, default_order_type=order_type
    )
