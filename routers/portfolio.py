from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from cronjobs.update_port import UpdatePort
from database.json_db import JsonDB
from models.portfolio import Portfolio
from models.db import PortfolioDB
from utils.constants import JSON_DB_PATH, SNP_TICKER
from utils.tables import PORTFOLIO_TABLE
from utils.funcs import get_stock_price_btwn

portfolio_router = APIRouter(prefix="/portfolio")
db = JsonDB(JSON_DB_PATH)


@portfolio_router.get("")
async def get_portfolio():
    u_port = UpdatePort(db)
    u_port.execute()
    portfolio: PortfolioDB = db.read_from_db(PortfolioDB, PORTFOLIO_TABLE)[0]

    snp_prices = get_stock_price_btwn(
        SNP_TICKER, [port_hist[0] for port_hist in portfolio.history]
    )
    port_init_v = portfolio.history[0][1]
    snp_portfolio_prices = [
        round(port_init_v * (snp_p / snp_prices[0]), 2) for snp_p in snp_prices
    ]

    ret = jsonable_encoder(portfolio)
    ret["snp"] = snp_portfolio_prices
    return ret


@portfolio_router.post("/init")
async def init_portfolio(portfolio: Portfolio):
    db.write_to_db(
        jsonable_encoder([PortfolioDB(buy_power=portfolio.cash)]),
        PORTFOLIO_TABLE,
    )
    return {"message": "Portfolio initialized"}
