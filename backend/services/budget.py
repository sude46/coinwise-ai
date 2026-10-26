from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.budget import BudgetRepository
from models.budget import Budget
from schemas.budget import BudgetCreate


class BudgetService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = BudgetRepository(session)

    async def create_budget(self, user_id: int, data: BudgetCreate) -> Budget:
        existing = await self.repo.get_by_user_month(
            user_id=user_id, year_month=data.year_month, category_id=data.category_id
        )
        if existing:
            raise ValueError("该月份/分类的预算已存在")
        budget = Budget(
            user_id=user_id,
            category_id=data.category_id,
            year_month=data.year_month,
            limit_amount=data.limit_amount,
        )
        return await self.repo.create(budget)

    async def list_budgets(
        self, user_id: int, year_month: Optional[str] = None
    ) -> List[Budget]:
        return await self.repo.list_by_user(user_id, year_month)

    async def get_budget(self, budget_id: int, user_id: int) -> Budget:
        budget = await self.repo.get_by_id(budget_id, user_id)
        if not budget:
            raise ValueError("预算不存在")
        return budget

    async def update_budget(self, budget_id: int, user_id: int, data: dict) -> Budget:
        budget = await self.get_budget(budget_id, user_id)
        return await self.repo.update(budget, data)

    async def delete_budget(self, budget_id: int, user_id: int) -> None:
        budget = await self.get_budget(budget_id, user_id)
        await self.repo.soft_delete(budget)