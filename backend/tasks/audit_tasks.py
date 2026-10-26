"""审计日志异步写入任务

所有敏感操作（增删改、登录注销、预算修改）通过 EventBus → Celery 异步写入 audit_logs，
不阻塞业务接口。
"""

from typing import Optional
from celery import shared_task
from celery.utils.log import get_task_logger

from infrastructure.db import async_session_master
from models.audit_log import AuditLog

logger = get_task_logger(__name__)


@shared_task(name="tasks.audit_tasks.write_audit_log", bind=True, max_retries=3)
def write_audit_log(
    self,
    user_id: int,
    action: str,
    resource: str,
    resource_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    request_id: Optional[str] = None,
    detail: Optional[str] = None,
):
    """异步写入审计日志"""
    import asyncio

    async def _run():
        async with async_session_master() as session:
            log = AuditLog(
                tenant_id=0,
                user_id=user_id or 0,
                action=action,
                resource=resource,
                resource_id=resource_id,
                ip_address=ip_address,
                user_agent=user_agent,
                request_id=request_id,
                detail=detail if isinstance(detail, str) else str(detail) if detail else None,
            )
            session.add(log)
            await session.commit()
            logger.info(f"Audit log written: {action} {resource}/{resource_id}")

    try:
        asyncio.run(_run())
    except Exception as exc:
        logger.error(f"Audit log write failed: {exc}")
        raise self.retry(exc=exc, countdown=30)
