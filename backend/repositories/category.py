from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.category import Category


class CategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, category: Category) -> Category:
        self.session.add(category)
        await self.session.flush()
        await self.session.refresh(category)
        return category

    async def get_by_id(self, category_id: int, user_id: Optional[int] = None) -> Optional[Category]:
        conditions = [Category.id == category_id, Category.is_deleted == False]
        if user_id is not None:
            conditions.append(Category.user_id == user_id)
        result = await self.session.execute(select(Category).where(*conditions))
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: int) -> List[Category]:
        result = await self.session.execute(
            select(Category).where(Category.user_id == user_id, Category.is_deleted == False)
        )
        return list(result.scalars().all())

    async def soft_delete(self, category: Category) -> None:
        category.is_deleted = True
        self.session.add(category)