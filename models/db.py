from datetime import datetime
from pydantic import BaseModel


class OpportunityDB(BaseModel):
    strategy_id: int
    timestamp: datetime
    ticker: str
    exchangeName: str
    order_type: int
    default_price: float
    metadata: dict
