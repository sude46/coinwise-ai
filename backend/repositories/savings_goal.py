from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from sqlalchemy import select, func, desc, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession
from models.savings_goal import SavingsGoal
from infrastructure.crypto import crypto


class SavingsGoalRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self._crypto = crypto

    def _encrypt(self, value: Optional[str]) -> Optional[str]:
        return self._crypto.encrypt(value) if value else value

    def _decrypt(self, value: Optional[str]) -> Optional[str]:
        return self._crypto.decrypt(value) if value else value

    def _decrypt_model(self, goal: SavingsGoal) -> SavingsGoal:
        if goal.name:
            goal.name = self._decrypt(goal.name)
        if goal.note:
            goal.note = self._decrypt(goal.note)
        return goal

    async def create(self, goal: SavingsGoal) -> SavingsGoal:
        if goal.name:
            goal.name = self._encrypt(goal.name)
        if goal.note:
            goal.note = self._encrypt(goal.note)
        self.session.add(goal)
        await self.session.flush()
        await self.session.refresh(goal)
        return self._decrypt_model(goal)

    async def get_by_id(self, goal_id: int, user_id: int) -> Optional[SavingsGoal]:
        result = await self.session.execute(
            select(SavingsGoal).where(
                SavingsGoal.id == goal_id,
                SavingsGoal.user_id == user_id,
                SavingsGoal.is_deleted == False,
            )
        )
        goal = result.scalar_one_or_none()
        return self._decrypt_model(goal) if goal else None

    async def list_by_user(
        self, user_id: int, status: Optional[str] = None, offset: int = 0, limit: int = 20
    ) -> tuple[List[SavingsGoal], int]:
        conditions = [SavingsGoal.user_id == user_id, SavingsGoal.is_deleted == False]
        if status:
            conditions.append(SavingsGoal.status == status)

        count_query = (
            select(func.count()).select_from(SavingsGoal).where(*conditions)
        )
        total = (await self.session.execute(count_query)).scalar() or 0

        query = (
            select(SavingsGoal)
            .where(*conditions)
            .order_by(desc(SavingsGoal.created_at))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(query)
        rows = result.scalars().all()
        return [self._decrypt_model(r) for r in rows], total

    async def update(self, goal: SavingsGoal, **kwargs) -> SavingsGoal:
        for key, value in kwargs.items():
            if hasattr(goal, key):
                if key in ("name", "note") and value is not None:
                    value = self._encrypt(value)
                setattr(goal, key, value)
        await self.session.flush()
        return self._decrypt_model(goal)

    async def soft_delete(self, goal: SavingsGoal, deleted_by: Optional[int] = None) -> None:
        goal.is_deleted = True
        goal.deleted_at = datetime.now()
        goal.deleted_by = deleted_by
        await self.session.flush()

    async def find_active_by_user(self, user_id: int) -> List[SavingsGoal]:
        result = await self.session.execute(
            select(SavingsGoal).where(
                SavingsGoal.user_id == user_id,
                SavingsGoal.status == "active",
                SavingsGoal.is_deleted == False,
            )
        )
        rows = result.scalars().all()
        return [self._decrypt_model(r) for r in rows]

    async def update_current_amount(self, goal_id: int, user_id: int, amount: Decimal) -> None:
        stmt = (
            sa_update(SavingsGoal)
            .where(SavingsGoal.id == goal_id, SavingsGoal.user_id == user_id)
            .values(current_amount=amount, updated_at=datetime.now())
        )
        await self.session.execute(stmt)
        await self.session.flush()
