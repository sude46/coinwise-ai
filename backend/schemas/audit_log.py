from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AuditLogOut(BaseModel):
    id: int
    user_id: int
    action: str
    resource: str
    resource_id: Optional[int]
    ip_address: Optional[str]
    user_agent: Optional[str]
    detail: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True