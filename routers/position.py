from typing import List, Tuple, Union
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from database.json_db import JsonDB
from models.position import Position
from models.db import OrderDB, PortfolioDB, PositionDB
from utils.constants import DEFAULT_EXCHANGE, JSON_DB_PATH
from utils.funcs import get_cur_stock_prices
from utils.tables import PORTFOLIO_TABLE, POSITION_TABLE

position_router = APIRouter(prefix="/position")
db = JsonDB(JSON_DB_PATH)


@position_router.get("")
async def get_positions():
    return jsonable_encoder(db.read_from_db(PositionDB, POSITION_TABLE))


@position_router.get("/clean")
async def clean_positions():
    db.write_to_db([], POSITION_TABLE)
    return {"message": "Positions cleaned"}


@position_router.post("/enter")
async def enter_position(enter_pos: Position):
    cur_price = get_cur_stock_prices(enter_pos.ticker).get(enter_pos.ticker, 0)
    portfolio: PortfolioDB = db.read_from_db(PortfolioDB, PORTFOLIO_TABLE)[0]

    if portfolio.buy_power < enter_pos.amount:
        raise HTTPException(
            status_code=400, detail="Not enough buy power to enter position"
        )

    enter_pos_quantity = enter_pos.amount / cur_price
    order = OrderDB(
        order_type=enter_pos.order_type,
        quantity=enter_pos_quantity,
        default_price=cur_price,
    )
    positions, current_pos = get_pos(enter_pos.ticker)
    portfolio.buy_power -= enter_pos.amount

    if current_pos == -1:
        positions.append(
            PositionDB(
                ticker=enter_pos.ticker, exchangeName=DEFAULT_EXCHANGE, orders=[order]
            )
        )
    else:
        positions[current_pos].orders.append(order)

    db.write_to_db([jsonable_encoder(portfolio)], PORTFOLIO_TABLE)
    db.write_to_db(jsonable_encoder(positions), POSITION_TABLE)
    return {"message": "Position entered"}


@position_router.post("/exit")
async def exit_position(exit_pos: Position):
    positions, current_pos = get_pos(exit_pos.ticker)
    portfolio: PortfolioDB = db.read_from_db(PortfolioDB, PORTFOLIO_TABLE)[0]
    cur_price = get_cur_stock_prices(exit_pos.ticker).get(exit_pos.ticker, 0)

    if current_pos != -1:
        # subtract quantity from the order where the order type is the same
        for order in positions[current_pos].orders:
            if exit_pos.amount == 0:
                break
            exit_pos_quantity = exit_pos.amount / order.default_price
            if order.order_type == exit_pos.order_type:
                negate = min(order.quantity, exit_pos_quantity)
                order.quantity -= negate
                exit_pos.amount -= negate * cur_price

        if exit_pos.amount > 0:
            raise HTTPException(
                status_code=400, detail="Not holding enough quantity to exit"
            )

        # remove the order if the quantity is 0
        positions[current_pos].orders = [
            order for order in positions[current_pos].orders if order.quantity > 0
        ]
        portfolio.buy_power += exit_pos.amount
        db.write_to_db([jsonable_encoder(portfolio)], PORTFOLIO_TABLE)
        db.write_to_db(jsonable_encoder(positions), POSITION_TABLE)
    else:
        raise HTTPException(status_code=400, detail="Position not found")

    return {"message": "Position exited"}


def get_pos(ticker: str) -> Tuple[List[PositionDB], int]:
    positions: List[PositionDB] = db.read_from_db(PositionDB, POSITION_TABLE)
    return positions, next(
        (i for i, pos in enumerate(positions) if pos.ticker == ticker), -1
    )
