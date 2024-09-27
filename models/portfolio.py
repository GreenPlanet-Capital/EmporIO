from pydantic import BaseModel


class Portfolio(BaseModel):
    cash: float
