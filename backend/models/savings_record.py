"""存钱流水关联表 — 解耦 transactions 与 savings_goals

transactions 通过弱关联 goal_id 指向计划，
同时 savings_records 记录每笔关联的存入金额，供异步对账使用。
"""

from sqlalchemy import Column, Integer, DECIMAL, DateTime, ForeignKey, func
from infrastructure.db import Base


class SavingsRecord(Base):
    __tablename__ = "savings_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, nullable=False, default=0, index=True, comment="租户ID，默认0")
    goal_id = Column(Integer, ForeignKey("savings_goals.id"), nullable=False, index=True, comment="存钱计划ID")
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False, index=True, comment="流水ID")
    amount = Column(DECIMAL(12, 2), nullable=False, comment="存入金额（冗余，与流水一致）")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
