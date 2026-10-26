from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean, func
from infrastructure.db import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    name = Column(String(50), nullable=False)
    account_type = Column(String(20), nullable=False, default="cash")
    balance = Column(Numeric(15, 2), nullable=False, default=0)
    icon = Column(String(10), nullable=True)
    is_default = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
