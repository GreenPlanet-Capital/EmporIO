from datetime import datetime
from typing import List, Tuple
from sqlmodel import JSON, Column, SQLModel, Field


class OpportunityDB(SQLModel, table=True):
    strategy_id: int
    timestamp: str
    ticker: str = Field(primary_key=True)
    exchangeName: str
    order_type: int
    default_price: float
    metadata_score: float


class OrderDB(SQLModel, table=False):
    order_type: int
    default_price: float
    avg_price: float = 0.0
    quantity: float


class PositionDB(SQLModel, table=True):
    email_address: str = Field(primary_key=True, foreign_key="userdb.email_address")
    ticker: str = Field(primary_key=True)
    exchangeName: str
    orders: List[OrderDB] = Field(default_factory=list, sa_column=Column(JSON))

    # Needed for Column(JSON)
    class Config:
        arbitrary_types_allowed = True


class HistoryDB(SQLModel, table=False):
    timestamp: str
    value: float


class PortfolioDB(SQLModel, table=True):
    email_address: str = Field(primary_key=True, foreign_key="userdb.email_address")
    value: float = 0.0
    history: List[HistoryDB] = Field(default_factory=list, sa_column=Column(JSON))
    buy_power: float

    # Needed for Column(JSON)
    class Config:
        arbitrary_types_allowed = True


class UserDB(SQLModel, table=True):
    email_address: str = Field(primary_key=True)
    hashed_password: str


class TokenDB(SQLModel, table=True):
    email_address: str = Field(primary_key=True)
    token: str
