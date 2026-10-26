"""储蓄目标模型 — 与交易记录完全解耦，通过事件驱动异步对账"""

from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey, Boolean, Text, func
from infrastructure.db import Base


class SavingsGoal(Base):
    __tablename__ = "savings_goals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, nullable=False, default=0, index=True, comment="租户ID，默认0")
    user_id = Column(Integer, nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True, comment="关联消费分类（用于冲突检测）")
    name = Column(String(100), nullable=False, comment="目标名称（密文存储）")
    target_amount = Column(DECIMAL(14, 2), nullable=False, comment="目标金额")
    current_amount = Column(DECIMAL(14, 2), default=0, comment="当前已储蓄金额（由定时任务异步更新，最终一致）")
    start_date = Column(DateTime(timezone=True), nullable=False, comment="目标开始日期")
    end_date = Column(DateTime(timezone=True), nullable=False, comment="目标截止日期")
    status = Column(String(20), default="active", comment="active/completed/cancelled")
    note = Column(Text, nullable=True, comment="备注（密文存储）")
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
