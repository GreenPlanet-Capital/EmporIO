from math import floor
from typing import List, Tuple, Union
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlmodel import delete, select, update
from models.position import Position
from models.db import OrderDB, PortfolioDB, PositionDB
from utils.constants import DEFAULT_EXCHANGE
from utils.funcs import get_cur_stock_prices
from utils.tables import PORTFOLIO_TABLE, POSITION_TABLE
from utils.db_conn import SessionDep, AuthDep, add_entity

# TODO: off by one 1 cent error when enter/exit position due to float precision or rounding
position_router = APIRouter(prefix="/position")


@position_router.get("")
async def get_positions(session: SessionDep, user: AuthDep):
    positions = session.exec(
        select(PositionDB).where(PositionDB.email_address == user.email_address)
    ).all()

    for pos in positions:
        pos.orders = [OrderDB(**order) for order in pos.orders]

        # aggregate all orders to get the avg price
        avg_price = 0

        for order in pos.orders:
            price_dt = get_cur_stock_prices(pos.ticker)
            avg_price += order.default_price
            order.default_price = price_dt.get(pos.ticker, 0)

        avg_price /= len(pos.orders)
        pos.orders[0].avg_price = avg_price

    return jsonable_encoder(positions)


@position_router.get("/clean")
async def clean_positions(session: SessionDep, user: AuthDep):
    session.exec(
        delete(PositionDB).where(PositionDB.email_address == user.email_address)
    )
    session.commit()
    return {"message": "Positions cleaned"}


@position_router.post("/enter")
async def enter_position(enter_pos: Position, session: SessionDep, user: AuthDep):
    if enter_pos.amount <= 0:
        raise HTTPException(
            status_code=400, detail="Amount must be greater than 0 to enter position"
        )
    elif enter_pos.order_type not in [0, 1]:
        raise HTTPException(
            status_code=400, detail="Order type must be 0 (buy) or 1 (sell)"
        )
    elif enter_pos.ticker == "":
        raise HTTPException(status_code=400, detail="Ticker must not be empty")

    cur_price = get_cur_stock_prices(enter_pos.ticker).get(enter_pos.ticker, 0)
    portfolio: PortfolioDB = session.get(PortfolioDB, user.email_address)

    if portfolio.buy_power < enter_pos.amount:
        raise HTTPException(
            status_code=400, detail="Not enough buy power to enter position"
        )

    enter_pos_quantity = enter_pos.amount / cur_price
    order = OrderDB(
        order_type=enter_pos.order_type,
        quantity=enter_pos_quantity,
        default_price=cur_price,
        avg_price=cur_price,
    )
    positions, cur_pos = get_pos(session, user.email_address, enter_pos.ticker)
    portfolio.buy_power -= enter_pos.amount

    if cur_pos == -1:
        new_pos = PositionDB(
            ticker=enter_pos.ticker,
            exchangeName=DEFAULT_EXCHANGE,
            orders=jsonable_encoder([order]),
            email_address=user.email_address,
        )
        add_entity(session, new_pos)
    else:
        pos = positions[cur_pos]
        pos.orders.append(order)

        session.exec(
            update(PositionDB)
            .where(PositionDB.email_address == user.email_address)
            .where(PositionDB.ticker == enter_pos.ticker)
            .values(orders=jsonable_encoder(pos.orders))
        )

    session.exec(
        update(PortfolioDB)
        .where(PortfolioDB.email_address == user.email_address)
        .values(buy_power=portfolio.buy_power)
    )
    session.commit()
    session.refresh(portfolio)

    return {"message": "Position entered"}


@position_router.post("/exit")
async def exit_position(exit_pos: Position, session: SessionDep, user: AuthDep):
    if exit_pos.amount <= 0:
        raise HTTPException(
            status_code=400, detail="Amount must be greater than 0 to exit position"
        )
    elif exit_pos.order_type not in [0, 1]:
        raise HTTPException(
            status_code=400, detail="Order type must be 0 (buy) or 1 (sell)"
        )
    elif exit_pos.ticker == "":
        raise HTTPException(status_code=400, detail="Ticker must not be empty")

    positions, current_pos = get_pos(session, user.email_address, exit_pos.ticker)
    portfolio: PortfolioDB = session.get(PortfolioDB, user.email_address)
    cur_price = get_cur_stock_prices(exit_pos.ticker).get(exit_pos.ticker, 0)
    orig_amt = exit_pos.amount

    positions[current_pos].orders = [
        OrderDB(**order) for order in positions[current_pos].orders
    ]

    if current_pos != -1:
        # subtract quantity from the order where the order type is the same
        for order in positions[current_pos].orders:
            if exit_pos.amount == 0:
                break

            exit_pos_quantity = exit_pos.amount / cur_price
            if order.order_type == exit_pos.order_type:
                negate = min(order.quantity, exit_pos_quantity)
                order.quantity -= negate
                exit_pos.amount -= negate * cur_price

        if exit_pos.amount > 0:
            raise HTTPException(
                status_code=400, detail="Not holding enough quantity to exit"
            )
        elif exit_pos.amount < 0:
            raise HTTPException(
                status_code=400, detail="Something went wrong with exiting position"
            )

        # remove the order if the quantity is 0
        positions[current_pos].orders = [
            jsonable_encoder(order)
            for order in positions[current_pos].orders
            if floor(order.quantity) > 0
        ]

        portfolio.buy_power += orig_amt

        session.exec(
            update(PortfolioDB)
            .where(PortfolioDB.email_address == user.email_address)
            .values(buy_power=portfolio.buy_power)
        )
        pos_exists = True

        if len(positions[current_pos].orders) == 0:
            session.exec(
                delete(PositionDB)
                .where(PositionDB.email_address == user.email_address)
                .where(PositionDB.ticker == exit_pos.ticker)
            )
            pos_exists = False
        else:
            session.exec(
                update(PositionDB)
                .where(PositionDB.email_address == user.email_address)
                .where(PositionDB.ticker == exit_pos.ticker)
                .values(orders=positions[current_pos].orders)
            )

        session.commit()
        if pos_exists:
            session.refresh(positions[current_pos])
        session.refresh(portfolio)
    else:
        raise HTTPException(status_code=400, detail="Position not found")

    return {"message": "Position exited"}


def get_pos(
    session: SessionDep, email_address: str, ticker: str
) -> Tuple[List[PositionDB], int]:
    positions = list(
        session.exec(
            select(PositionDB).where(PositionDB.email_address == email_address)
        ).all()
    )
    return positions, next(
        (i for i, pos in enumerate(positions) if pos.ticker == ticker), -1
    )
