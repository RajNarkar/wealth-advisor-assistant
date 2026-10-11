from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class Asset(BaseModel):
    type: Literal["equity", "bond", "cash", "mutual_fund", "real_estate", "crypto"]
    ticker: str
    value: float
    weight: float

class Portfolio(BaseModel):
    total_value: float
    assets: List[Asset]

class Transaction(BaseModel):
    txn_id: str
    date: str
    type: Literal["buy", "sell", "transfer", "deposit", "withdrawal"]
    ticker: str
    amount: float

class ClientData(BaseModel):
    client_id: str
    name: str
    age: int
    risk_profile: Literal["conservative", "moderate", "aggressive"]
    portfolio: Portfolio
    transactions: List[Transaction]
    goals: List[str] = Field(default_factory=list)
    annual_income: float
