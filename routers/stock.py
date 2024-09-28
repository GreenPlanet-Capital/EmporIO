from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from database.json_db import JsonDB
from models.db import OpportunityDB
from utils.constants import JSON_DB_PATH
from utils.tables import OPPORTUNITY_TABLE

stock_router = APIRouter(prefix="/stock")
db = JsonDB(JSON_DB_PATH)


@stock_router.get("")
async def get_stock(ticker: str):
    opps: List[OpportunityDB] = db.read_from_db(OpportunityDB, OPPORTUNITY_TABLE)
    opp = next((x for x in opps if x.ticker == ticker), None)

    if opp is not None:
        return jsonable_encoder(opp)

    raise HTTPException(status_code=404, detail="Stock not found")
