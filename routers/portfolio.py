from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from cronjobs.update_port import UpdatePort
from database.json_db import JsonDB
from models.portfolio import Portfolio
from models.db import PortfolioDB
from utils.constants import JSON_DB_PATH
from utils.tables import PORTFOLIO_TABLE

portfolio_router = APIRouter(prefix="/portfolio")
db = JsonDB(JSON_DB_PATH)


@portfolio_router.get("")
async def get_portfolio():
    u_port = UpdatePort(db)
    u_port.execute()
    return jsonable_encoder(db.read_from_db(PortfolioDB, PORTFOLIO_TABLE)[0])


@portfolio_router.post("/init")
async def init_portfolio(portfolio: Portfolio):
    db.write_to_db(
        jsonable_encoder([PortfolioDB(buy_power=portfolio.cash)]),
        PORTFOLIO_TABLE,
    )
    return {"message": "Portfolio initialized"}
