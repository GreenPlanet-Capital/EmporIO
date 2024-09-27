from typing import Dict, List
from Quantify.tools.live_tester import LiveTester
from Quantify.strats.macd_rsi_boll import Macd_Rsi_Boll
from Quantify.constants.timeframe import TimeFrame
from Quantify.positions.opportunity import Opportunity
import pandas as pd
from utils.constants import DEFAULT_LOOKBACK


class QuantifyIntegrator:
    def __init__(
        self,
        symbols: List[str],
        dict_stock_df: Dict[str, pd.DataFrame],
        exchange_name: str,
        num_recommendations: int,
        percent_long: float,
    ) -> None:
        strat = Macd_Rsi_Boll(
            sid=1, name="macd_rsi_boll", timeframe=TimeFrame(100, DEFAULT_LOOKBACK), lookback=DEFAULT_LOOKBACK
        )
        self.tester_l = LiveTester(
            list_of_final_symbols=symbols,
            dict_of_dfs=dict_stock_df,
            exchangeName=exchange_name,
            strat=strat,
            num_top=num_recommendations,
            percent_l=percent_long,
        )

    def get_positions(self) -> List[Opportunity]:
        return self.tester_l.execute_strat()
