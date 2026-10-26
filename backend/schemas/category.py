from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CategoryCreate(BaseModel):
    name: str
    icon: Optional[str] = None

class CategoryOut(BaseModel):
    id: int
    user_id: int
    name: str
    icon: Optional[str]
    is_system: bool
    created_at: datetime

    class Config:
        from_attributes = True