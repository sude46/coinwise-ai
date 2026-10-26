from typing import Optional
from datetime import datetime
from models.audit_log import AuditLog
from repositories.audit_log import AuditLogRepository
from schemas.audit_log import AuditLogOut


class AuditLogService:
    def __init__(self, repo: AuditLogRepository):
        self._repo = repo

    async def write(
        self,
        user_id: int,
        action: str,
        resource: str,
        resource_id: Optional[int] = None,
        detail: Optional[str] = None,
    ) -> AuditLogOut:
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            detail=detail,
        )
        saved = await self._repo.create(log)
        return AuditLogOut.model_validate(saved)

    async def list_for_user(
        self,
        user_id: int,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[AuditLogOut], int]:
        rows, total = await self._repo.list_by_user(
            user_id=user_id,
            action=action,
            resource=resource,
            start_date=start_date,
            end_date=end_date,
            offset=offset,
            limit=limit,
        )
        return [AuditLogOut.model_validate(r) for r in rows], total