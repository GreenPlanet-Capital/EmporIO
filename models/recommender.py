from pydantic import BaseModel


class Recommendation(BaseModel):
    ticker: str
    score: float
    order_type: str
