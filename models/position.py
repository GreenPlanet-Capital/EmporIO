from pydantic import BaseModel


class Position(BaseModel):
    ticker: str
    order_type: int
    quantity: float
