from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, log: AuditLog) -> AuditLog:
        self.session.add(log)
        await self.session.flush()
        await self.session.refresh(log)
        return log

    async def list_by_user(
        self,
        user_id: int,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[List[AuditLog], int]:
        conditions = [AuditLog.user_id == user_id]
        if action:
            conditions.append(AuditLog.action == action)
        if resource:
            conditions.append(AuditLog.resource == resource)
        if start_date:
            conditions.append(AuditLog.created_at >= start_date)
        if end_date:
            conditions.append(AuditLog.created_at <= end_date)

        count_query = select(func.count()).select_from(AuditLog).where(*conditions)
        total = (await self.session.execute(count_query)).scalar() or 0

        query = (
            select(AuditLog)
            .where(*conditions)
            .order_by(desc(AuditLog.created_at))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(query)
        rows = result.scalars().all()
        return list(rows), total