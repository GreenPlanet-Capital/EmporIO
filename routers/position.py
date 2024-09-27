from typing import List, Tuple, Union
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from database.json_db import JsonDB
from models.position import Position
from models.db import OpportunityDB, OrderDB, PositionDB
from utils.constants import DEFAULT_EXCHANGE, JSON_DB_PATH
from utils.tables import POSITION_TABLE

position_router = APIRouter(prefix="/position")
db = JsonDB(JSON_DB_PATH)


@position_router.post("/enter")
async def enter_pos(enter_pos: Position):
    order = OrderDB(
        order_type=enter_pos.order_type,
        quantity=enter_pos.quantity,
        default_price=get_stock_price(enter_pos.ticker),
    )
    positions, current_pos = get_pos(enter_pos.ticker)

    if current_pos == -1:
        positions.append(
            PositionDB(
                ticker=enter_pos.ticker, exchangeName=DEFAULT_EXCHANGE, orders=[order]
            )
        )
    else:
        positions[current_pos].orders.append(order)

    db.write_to_db(POSITION_TABLE, jsonable_encoder(positions))
    return {"message": "Position entered"}


@position_router.post("/exit")
async def exit_pos(exit_pos: Position):
    positions, current_pos = get_pos(exit_pos.ticker)

    if current_pos != -1:
        # subtract quantity from the order where the order type is the same
        for order in positions[current_pos].orders:
            if exit_pos.quantity == 0:
                break

            if order.order_type == exit_pos.order_type:
                negate = min(order.quantity, exit_pos.quantity)
                order.quantity -= negate
                exit_pos.quantity -= negate

        if exit_pos.quantity > 0:
            raise HTTPException(
                status_code=400, detail="Not holding enough quantity to exit"
            )

        # remove the order if the quantity is 0
        positions[current_pos].orders = [
            order for order in positions[current_pos].orders if order.quantity > 0
        ]
        db.write_to_db(POSITION_TABLE, jsonable_encoder(positions))
    else:
        raise HTTPException(status_code=400, detail="Position not found")

    return {"message": "Position exited"}


def get_stock_price(ticker: str) -> float:
    opportunities: List[OpportunityDB] = db.read_from_db(OpportunityDB, "opportunity")
    for opp in opportunities:
        if opp.ticker == ticker:
            return opp.default_price
    return 0.0


def get_pos(ticker: str) -> Tuple[List[PositionDB], int]:
    positions: List[PositionDB] = db.read_from_db(PositionDB, POSITION_TABLE)
    return positions, next(
        (i for i, pos in enumerate(positions) if pos.ticker == ticker), -1
    )
