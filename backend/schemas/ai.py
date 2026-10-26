from typing import Optional
from pydantic import BaseModel


class AIChatRequest(BaseModel):
    intent: str = "general"
    text: str = ""
    category_id: Optional[int] = None
    amount: Optional[float] = None
    transaction_date: Optional[str] = None
    conversation_id: Optional[str] = None
