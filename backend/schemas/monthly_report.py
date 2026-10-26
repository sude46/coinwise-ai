from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class MonthlyReportOut(BaseModel):
    id: int
    user_id: int
    year_month: str
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal
    created_at: datetime

    class Config:
        from_attributes = True