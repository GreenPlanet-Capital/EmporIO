from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from database.json_db import JsonDB
from models.portfolio import Portfolio
from models.db import PortfolioDB
from utils.constants import JSON_DB_PATH
from utils.tables import PORTFOLIO_TABLE

portfolio_router = APIRouter(prefix="/portfolio")
db = JsonDB(JSON_DB_PATH)


@portfolio_router.get("")
async def get_portfolio():
    return jsonable_encoder(db.read_from_db(PortfolioDB, PORTFOLIO_TABLE))


@portfolio_router.post("/init")
async def init_portfolio(portfolio: Portfolio):
    db.write_to_db(
        PORTFOLIO_TABLE, jsonable_encoder(PortfolioDB(buy_power=portfolio.cash))
    )
