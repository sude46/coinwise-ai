from typing import List, Optional
from decimal import Decimal
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from models.savings_record import SavingsRecord


class SavingsRecordRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, goal_id: int, transaction_id: int, amount: Decimal, tenant_id: int = 0) -> SavingsRecord:
        record = SavingsRecord(
            tenant_id=tenant_id,
            goal_id=goal_id,
            transaction_id=transaction_id,
            amount=amount,
        )
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def get_by_id(self, record_id: int) -> Optional[SavingsRecord]:
        result = await self.session.execute(
            select(SavingsRecord).where(SavingsRecord.id == record_id)
        )
        return result.scalar_one_or_none()

    async def list_by_goal(self, goal_id: int, offset: int = 0, limit: int = 100) -> List[SavingsRecord]:
        result = await self.session.execute(
            select(SavingsRecord)
            .where(SavingsRecord.goal_id == goal_id)
            .order_by(desc(SavingsRecord.created_at))
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def sum_amount_by_goal(self, goal_id: int) -> Decimal:
        result = await self.session.execute(
            select(func.coalesce(func.sum(SavingsRecord.amount), 0)).where(
                SavingsRecord.goal_id == goal_id
            )
        )
        return result.scalar() or Decimal("0")

    async def delete_by_transaction(self, transaction_id: int) -> None:
        """当流水被删除/修改时，删除关联记录（由对账任务重新计算）"""
        from sqlalchemy import delete
        await self.session.execute(
            delete(SavingsRecord).where(SavingsRecord.transaction_id == transaction_id)
        )
