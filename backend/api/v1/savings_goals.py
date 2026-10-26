from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db, get_write_db
from schemas.savings_goal import SavingsGoalCreate, SavingsGoalUpdate, SavingsGoalOut, SavingsGoalPredictOut
from schemas.common import PaginatedResponse
from services.savings_goal import SavingsGoalService
from repositories.savings_goal import SavingsGoalRepository
from repositories.savings_record import SavingsRecordRepository
from models.user import User
from core.exceptions import NotFoundException
from typing import Optional

router = APIRouter(tags=["储蓄目标"])


def _get_service(db: AsyncSession) -> SavingsGoalService:
    return SavingsGoalService(
        SavingsGoalRepository(db),
        SavingsRecordRepository(db),
    )


@router.post("", response_model=SavingsGoalOut, status_code=status.HTTP_201_CREATED)
async def create_savings_goal(
    payload: SavingsGoalCreate,
    db: AsyncSession = Depends(get_write_db),
    current_user: User = Depends(get_current_user),
):
    service = _get_service(db)
    return await service.create(current_user.id, payload)


@router.get("", response_model=PaginatedResponse[SavingsGoalOut])
async def list_savings_goals(
    status: Optional[str] = Query(None, pattern="^(active|completed|cancelled)$"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = _get_service(db)
    offset = (page - 1) * size
    items, total = await service.list_for_user(current_user.id, status, offset, size)
    return PaginatedResponse(items=items, total=total, page=page, size=size)


@router.get("/{goal_id}", response_model=SavingsGoalOut)
async def get_savings_goal(
    goal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = _get_service(db)
    try:
        return await service.get(goal_id, current_user.id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{goal_id}/predict", response_model=SavingsGoalPredictOut)
async def predict_savings_goal(
    goal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """基于 EMA 预测存钱计划达成情况"""
    service = _get_service(db)
    try:
        return await service.predict_achievement(goal_id, current_user.id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{goal_id}", response_model=SavingsGoalOut)
async def update_savings_goal(
    goal_id: int,
    payload: SavingsGoalUpdate,
    db: AsyncSession = Depends(get_write_db),
    current_user: User = Depends(get_current_user),
):
    service = _get_service(db)
    try:
        return await service.update(goal_id, current_user.id, payload)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_savings_goal(
    goal_id: int,
    db: AsyncSession = Depends(get_write_db),
    current_user: User = Depends(get_current_user),
):
    service = _get_service(db)
    try:
        await service.delete(goal_id, current_user.id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
