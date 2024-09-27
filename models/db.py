from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class OpportunityDB(BaseModel):
    strategy_id: int
    timestamp: datetime
    ticker: str
    exchangeName: str
    order_type: int
    default_price: float
    metadata: dict


class OrderDB(BaseModel):
    order_type: int
    default_price: float
    quantity: int


class PositionDB(BaseModel):
    ticker: str
    exchangeName: str
    orders: List[OrderDB] = Field(default_factory=list)


class PortfolioDB(BaseModel):
    history: List[float] = Field(default_factory=list)
    buy_power: float
    