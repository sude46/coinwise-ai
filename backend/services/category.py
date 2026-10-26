from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.category import CategoryRepository
from models.category import Category
from schemas.category import CategoryCreate


class CategoryService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = CategoryRepository(session)

    async def create_category(self, user_id: int, data: CategoryCreate) -> Category:
        category = Category(user_id=user_id, name=data.name, icon=data.icon)
        return await self.repo.create(category)

    async def list_categories(self, user_id: int) -> List[Category]:
        return await self.repo.list_by_user(user_id)

    async def get_category(self, category_id: int, user_id: int) -> Category:
        category = await self.repo.get_by_id(category_id, user_id)
        if not category:
            raise ValueError("分类不存在")
        return category

    async def delete_category(self, category_id: int, user_id: int) -> None:
        category = await self.get_category(category_id, user_id)
        if category.is_system:
            raise ValueError("系统分类不可删除")
        await self.repo.soft_delete(category)