from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey, func
from infrastructure.db import Base

class MonthlyReport(Base):
    __tablename__ = "monthly_reports"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    year_month = Column(String(7), nullable=False, comment="YYYY-MM")
    total_income = Column(DECIMAL(12, 2), default=0)
    total_expense = Column(DECIMAL(12, 2), default=0)
    balance = Column(DECIMAL(12, 2), default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())