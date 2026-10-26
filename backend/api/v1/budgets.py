"""预算设置 + 进度查询"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db, get_write_db, get_current_user
from schemas.budget import BudgetCreate, BudgetUpdate, BudgetOut
from services.budget import BudgetService
from models.user import User

router = APIRouter()


@router.post("", response_model=BudgetOut, status_code=status.HTTP_201_CREATED)
async def create_budget(
    payload: BudgetCreate,
    db: AsyncSession = Depends(get_write_db),
    current_user: User = Depends(get_current_user),
):
    """创建预算（factory context manager 自动 commit）"""
    service = BudgetService(db)
    try:
        return await service.create_budget(current_user.id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=List[BudgetOut])
async def list_budgets(
    year_month: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """查询预算列表"""
    service = BudgetService(db)
    return await service.list_budgets(current_user.id, year_month)


@router.get("/{budget_id}", response_model=BudgetOut)
async def get_budget(
    budget_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取单条预算"""
    service = BudgetService(db)
    try:
        return await service.get_budget(budget_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{budget_id}", response_model=BudgetOut)
async def update_budget(
    budget_id: int,
    payload: BudgetUpdate,
    db: AsyncSession = Depends(get_write_db),
    current_user: User = Depends(get_current_user),
):
    service = BudgetService(db)
    try:
        return await service.update_budget(budget_id, current_user.id, payload.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    budget_id: int,
    db: AsyncSession = Depends(get_write_db),
    current_user: User = Depends(get_current_user),
):
    """删除预算（factory context manager 自动 commit）"""
    service = BudgetService(db)
    try:
        await service.delete_budget(budget_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
