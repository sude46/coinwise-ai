"""审计日志模型"""

from sqlalchemy import Column, Integer, String, DateTime, Text, func
from infrastructure.db import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, nullable=False, default=0, index=True, comment="租户ID，默认0")
    user_id = Column(Integer, nullable=False, index=True, comment="操作者ID，0表示系统操作")
    action = Column(String(50), nullable=False, comment="操作类型: CREATE/UPDATE/DELETE/LOGIN/EXPORT")
    resource = Column(String(50), nullable=False, comment="操作资源: transaction/account/budget等")
    resource_id = Column(Integer, nullable=True, comment="资源ID")
    ip_address = Column(String(45), nullable=True, comment="客户端IP")
    user_agent = Column(String(256), nullable=True, comment="User-Agent")
    request_id = Column(String(64), nullable=True, index=True, comment="请求追踪ID")
    detail = Column(Text, nullable=True, comment="操作详情JSON")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
