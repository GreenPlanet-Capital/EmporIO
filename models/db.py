from datetime import datetime
from typing import List, Tuple
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
    quantity: float


class PositionDB(BaseModel):
    ticker: str
    exchangeName: str
    orders: List[OrderDB] = Field(default_factory=list)


class PortfolioDB(BaseModel):
    value: float = 0.0
    history: List[Tuple[str, float]] = Field(default_factory=list)
    buy_power: float
