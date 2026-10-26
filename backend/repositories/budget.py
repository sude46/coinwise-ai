from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.budget import Budget


class BudgetRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, budget: Budget) -> Budget:
        self.session.add(budget)
        await self.session.flush()
        await self.session.refresh(budget)
        return budget

    async def get_by_id(self, budget_id: int, user_id: Optional[int] = None) -> Optional[Budget]:
        conditions = [Budget.id == budget_id, Budget.is_deleted == False]
        if user_id is not None:
            conditions.append(Budget.user_id == user_id)
        result = await self.session.execute(select(Budget).where(*conditions))
        return result.scalar_one_or_none()

    async def get_by_user_month(
        self, user_id: int, year_month: str, category_id: Optional[int] = None
    ) -> Optional[Budget]:
        conditions = [
            Budget.user_id == user_id,
            Budget.year_month == year_month,
            Budget.is_deleted == False,
        ]
        if category_id is not None:
            conditions.append(Budget.category_id == category_id)
        result = await self.session.execute(select(Budget).where(*conditions))
        return result.scalar_one_or_none()

    async def list_by_user(
        self, user_id: int, year_month: Optional[str] = None
    ) -> List[Budget]:
        conditions = [Budget.user_id == user_id, Budget.is_deleted == False]
        if year_month is not None:
            conditions.append(Budget.year_month == year_month)
        result = await self.session.execute(select(Budget).where(*conditions))
        return list(result.scalars().all())

    async def update(self, budget: Budget, update_data: dict) -> Budget:
        for key, value in update_data.items():
            if value is not None:
                setattr(budget, key, value)
        self.session.add(budget)
        return budget

    async def soft_delete(self, budget: Budget) -> None:
        budget.is_deleted = True
        self.session.add(budget)