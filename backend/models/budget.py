from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey, Boolean, func
from infrastructure.db import Base

class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    year_month = Column(String(7), nullable=False, comment="YYYY-MM")
    limit_amount = Column(DECIMAL(12, 2), nullable=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())