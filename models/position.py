from pydantic import BaseModel


class Position(BaseModel):
    ticker: str
    order_type: int
    amount: float
