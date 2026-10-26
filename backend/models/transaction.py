from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey, Boolean, Text, func, Index
from sqlalchemy.orm import relationship
from infrastructure.db import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, nullable=False, default=0, index=True, comment="租户ID，默认0")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    account_id = Column(Integer, ForeignKey("accounts.id"))
    goal_id = Column(Integer, ForeignKey("savings_goals.id"), nullable=True, index=True, comment="关联存钱计划（可空，弱关联）")
    type = Column(String(10), nullable=False, comment="income/expense")
    amount = Column(DECIMAL(12, 2), nullable=False)
    remark = Column(Text, comment="备注（密文存储）")
    source = Column(String(20), nullable=False, default="manual", comment="来源: manual/ai/import")
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)

    category = relationship("Category", lazy="selectin")

    __table_args__ = (
        Index("idx_tenant_user_date", "tenant_id", "user_id", "transaction_date", "type"),
        Index("idx_tenant_user_category", "tenant_id", "user_id", "category_id", "transaction_date"),
        Index("idx_tenant_user_goal", "tenant_id", "user_id", "goal_id", "transaction_date"),
        Index("idx_tenant_user_source", "tenant_id", "user_id", "source", "created_at"),
    )
