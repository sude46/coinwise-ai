from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional
from decimal import Decimal


class SavingsGoalCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    target_amount: Decimal = Field(..., gt=0)
    category_id: Optional[int] = None
    start_date: datetime
    end_date: datetime
    note: Optional[str] = None


class SavingsGoalUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    target_amount: Optional[Decimal] = Field(default=None, gt=0)
    category_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = Field(default=None, pattern="^(active|completed|cancelled)$")
    note: Optional[str] = None


class SavingsGoalOut(BaseModel):
    id: int
    user_id: int
    category_id: Optional[int]
    name: str
    target_amount: Decimal
    current_amount: Decimal
    start_date: datetime
    end_date: datetime
    status: str
    note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class SavingsGoalPredictOut(BaseModel):
    goal_id: int
    daily_required: float
    predicted_date: Optional[date] = None
    risk: str  # low/medium/high/critical/unknown/expired
    message: str
    ema_daily_avg: float

    class Config:
        from_attributes = True
