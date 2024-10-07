from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from database.json_db import JsonDB
from models.db import OpportunityDB
from utils.constants import JSON_DB_PATH
from utils.funcs import create_stock_graph, get_cur_stock_prices
from utils.tables import OPPORTUNITY_TABLE

stock_router = APIRouter(prefix="/stock")


@stock_router.get("")
async def get_stock(ticker: str):
    price_dt = get_cur_stock_prices(ticker)

    if price_dt:
        return jsonable_encoder({"ticker": ticker, "close": price_dt[ticker]})

    raise HTTPException(status_code=404, detail="Stock not found")


@stock_router.get("/graph")
async def get_stock_graph(ticker: str):
    try:
        fig = create_stock_graph(ticker)
        return fig.to_json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
