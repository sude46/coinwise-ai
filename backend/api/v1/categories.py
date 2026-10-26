"""收支分类管理"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db, get_write_db, get_current_user
from schemas.category import CategoryCreate, CategoryOut
from services.category import CategoryService
from models.user import User

router = APIRouter()


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoryCreate,
    db: AsyncSession = Depends(get_write_db),
    current_user: User = Depends(get_current_user),
):
    """创建分类（factory context manager 自动 commit）"""
    service = CategoryService(db)
    return await service.create_category(current_user.id, payload)


@router.get("", response_model=List[CategoryOut])
async def list_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前用户分类列表"""
    service = CategoryService(db)
    return await service.list_categories(current_user.id)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_write_db),
    current_user: User = Depends(get_current_user),
):
    """删除分类（系统分类不可删除，factory context manager 自动 commit）"""
    service = CategoryService(db)
    try:
        await service.delete_category(category_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
