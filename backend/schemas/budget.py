from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal


class BudgetCreate(BaseModel):
    category_id: Optional[int] = None
    year_month: str = Field(..., pattern=r"^\d{4}-\d{2}$")
    limit_amount: Decimal = Field(..., gt=0)


class BudgetUpdate(BaseModel):
    category_id: Optional[int] = None
    year_month: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}$")
    limit_amount: Optional[Decimal] = Field(None, gt=0)


class BudgetOut(BaseModel):
    id: int
    user_id: int
    category_id: Optional[int]
    year_month: str
    limit_amount: Decimal
    created_at: datetime

    class Config:
        from_attributes = True