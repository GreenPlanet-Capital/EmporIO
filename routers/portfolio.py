from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
import pytz
from cronjobs.update_port import UpdatePort
from models.portfolio import Portfolio
from models.db import HistoryDB, PortfolioDB
from utils.constants import SNP_TICKER
from utils.funcs import get_stock_price_btwn
from utils.db_conn import SessionDep, AuthDep, add_entity, global_db

portfolio_router = APIRouter(prefix="/portfolio")


@portfolio_router.get("")
async def get_portfolio(session: SessionDep, user: AuthDep):
    u_port = UpdatePort(global_db)
    u_port.execute()
    portfolio: PortfolioDB = session.get(PortfolioDB, user.email_address)
    portfolio.history = [HistoryDB(**hist) for hist in portfolio.history]

    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    try:
        snp_prices = get_stock_price_btwn(
            SNP_TICKER, [port_hist.timestamp for port_hist in portfolio.history]
        )
    except Exception as e:
        print("Error getting snp prices", e)
        snp_prices = [portfolio.value]

    port_init_v = portfolio.history[0].value
    snp_portfolio_prices = [
        port_init_v * (snp_p / snp_prices[0]) for snp_p in snp_prices
    ]

    ret = jsonable_encoder(portfolio)
    ret["snp"] = snp_portfolio_prices
    return ret


@portfolio_router.post("/init")
async def init_portfolio(portfolio: Portfolio, session: SessionDep, user: AuthDep):
    exists_portfolio = session.get(PortfolioDB, user.email_address)
    if exists_portfolio:
        raise HTTPException(status_code=400, detail="Portfolio already initialized")

    portfolio_data = PortfolioDB(
        email_address=user.email_address,
        value=portfolio.cash,
        buy_power=portfolio.cash,
        history=[
            jsonable_encoder(
                HistoryDB(
                    timestamp=datetime.now(tz=pytz.timezone("US/Eastern")).strftime(
                        "%Y-%m-%d"
                    ),
                    value=portfolio.cash,
                )
            )
        ],
    )
    add_entity(session, portfolio_data)
    return {"message": "Portfolio initialized"}
