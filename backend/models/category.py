from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from infrastructure.db import Base

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    icon = Column(String(50))
    is_system = Column(Boolean, default=False)  # 系统预置分类不可删除
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())