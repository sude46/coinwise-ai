from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime


class AccountCreate(BaseModel):
    name: str
    account_type: str = "cash"
    balance: Decimal = Decimal("0")
    icon: Optional[str] = None
    is_default: bool = False


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    account_type: Optional[str] = None
    balance: Optional[Decimal] = None
    icon: Optional[str] = None
    is_default: Optional[bool] = None


class AccountOut(BaseModel):
    id: int
    user_id: int
    name: str
    account_type: str
    balance: Decimal
    icon: Optional[str]
    is_default: bool
    created_at: datetime

    class Config:
        from_attributes = True
