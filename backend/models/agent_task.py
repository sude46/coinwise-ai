from sqlalchemy import Column, Integer, String, DateTime, Text, func
from infrastructure.db import Base


class AgentTask(Base):
    __tablename__ = "agent_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    task_type = Column(String(50), nullable=False, comment="任务类型: classify/alert/report")
    pending_id = Column(String(64), unique=True, nullable=False, comment="幂等键 MD5")
    status = Column(String(20), default="pending", comment="pending/running/success/failed")
    payload = Column(Text, comment="任务参数 JSON")
    result = Column(Text, comment="执行结果 JSON")
    error_msg = Column(Text, comment="错误信息")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
