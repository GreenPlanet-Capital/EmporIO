from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from database.json_db import JsonDB
from models.db import OpportunityDB
from utils.constants import JSON_DB_PATH
from utils.funcs import get_cur_stock_prices
from utils.tables import OPPORTUNITY_TABLE

stock_router = APIRouter(prefix="/stock")


@stock_router.get("")
async def get_stock(ticker: str):
    price_dt = get_cur_stock_prices(ticker)

    if price_dt:
        return jsonable_encoder({"ticker": ticker, "close": price_dt[ticker]})

    raise HTTPException(status_code=404, detail="Stock not found")
