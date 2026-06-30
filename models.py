from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel


class Subscription(BaseModel):
    customer_id: str
    start_date: date
    end_date: Optional[date] = None
    plan: str
    monthly_price: float


class MRREntry(BaseModel):
    start_date: date
    end_date: date
    mrr: float


class ChurnEntry(BaseModel):
    start_date: date
    end_date: date
    churned_customers: int
