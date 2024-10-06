from dataclasses import dataclass
from fastapi.encoders import jsonable_encoder
import requests
from models.db import OpportunityDB
from models.portfolio import Portfolio
from models.recommender import Recommendation
from models.position import Position

HOST = "http://localhost:8000"
NUM_POS = 5
LIMIT = 100


@dataclass
class Stock:
    ticker: str
    close: float


def set_portfolio(portfolio: Portfolio):
    response = requests.post(f"{HOST}/portfolio/init", json=jsonable_encoder(portfolio))
    return response.json()


def get_portfolio():
    response = requests.get(f"{HOST}/portfolio")
    return response.json()


def get_recommendation():
    response = requests.get(f"{HOST}/recommend?limit={LIMIT}")
    return response.json()


def get_recom_positions():
    recom_json = get_recommendation()
    return [Recommendation(**rec) for rec in recom_json]


def get_stock(ticker: str):
    response = requests.get(f"{HOST}/stock?ticker={ticker}")
    return Stock(**response.json()) if response.status_code == 200 else None


def clean_pos():
    response = requests.get(f"{HOST}/position/clean")
    return response.json()


def acquire_pos(amt_per_pos: int):
    rec_pos = get_recom_positions()
    acq_pos = []
    num_acq = 0

    for pos in rec_pos:
        if num_acq >= NUM_POS:
            break

        resp = requests.post(
            f"{HOST}/position/enter",
            json=jsonable_encoder(
                Position(
                    ticker=pos.ticker,
                    order_type=pos.order_type,
                    amount=amt_per_pos,
                )
            ),
        )

        if resp.status_code == 200:
            acq_pos.append(pos)
            num_acq += 1

    return acq_pos


print(clean_pos())

print(set_portfolio(Portfolio(cash=1000)))

print(acquire_pos(amt_per_pos=100))

print(get_portfolio())
