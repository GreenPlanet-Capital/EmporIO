from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from integration.datamgr import DataMgrIntegrator
from utils.constants import DEFAULT_EXCHANGE
from utils.funcs import create_stock_graph, get_cur_stock_prices

stock_router = APIRouter(prefix="/stock")


@stock_router.get("")
async def get_stock(ticker: str):
    price_dt = get_cur_stock_prices(ticker)

    if price_dt:
        return jsonable_encoder({"ticker": ticker, "close": price_dt[ticker]})

    raise HTTPException(status_code=404, detail="Stock not found")


@stock_router.get("/graph")
async def get_stock_graph(ticker: str, order_type: int):
    try:
        fig = create_stock_graph(ticker, order_type)
        return fig.to_json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@stock_router.get("/list")
async def get_stock_list():
    data_mgr = DataMgrIntegrator(
        exchange_name=DEFAULT_EXCHANGE, limit=None, update_tickers=False
    )
    return jsonable_encoder(sorted(data_mgr.get_list_symbols()))
