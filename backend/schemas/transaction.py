from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal

from schemas.category import CategoryOut


class TransactionCreate(BaseModel):
    category_id: Optional[int] = None
    account_id: Optional[int] = None
    goal_id: Optional[int] = None
    type: str = Field(..., pattern="^(income|expense)$")
    amount: Decimal = Field(..., gt=0)
    remark: Optional[str] = None
    source: Optional[str] = Field(default="manual", pattern="^(manual|ai|import)$")
    transaction_date: datetime


class TransactionUpdate(BaseModel):
    category_id: Optional[int] = None
    account_id: Optional[int] = None
    goal_id: Optional[int] = None
    amount: Optional[Decimal] = Field(default=None, gt=0)
    remark: Optional[str] = None
    transaction_date: Optional[datetime] = None


class TransactionOut(BaseModel):
    id: int
    user_id: int
    category_id: Optional[int]
    account_id: Optional[int]
    goal_id: Optional[int]
    category: Optional[CategoryOut] = None
    type: str
    amount: Decimal
    remark: Optional[str]
    source: str
    transaction_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True
