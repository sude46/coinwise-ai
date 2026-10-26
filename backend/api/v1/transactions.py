"""记账 CRUD + 流水查询"""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db, get_write_db, get_current_user
from schemas.transaction import TransactionCreate, TransactionUpdate, TransactionOut
from schemas.common import PaginatedResponse
from services.transaction import TransactionService
from models.user import User

router = APIRouter()


@router.post("", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    payload: TransactionCreate,
    db: AsyncSession = Depends(get_write_db),
    current_user: User = Depends(get_current_user),
):
    """创建记账记录（factory context manager 自动 commit）"""
    service = TransactionService(db)
    return await service.create_transaction(current_user.id, payload)


@router.get("", response_model=PaginatedResponse[TransactionOut])
async def list_transactions(
    category_id: Optional[int] = Query(None),
    type_: Optional[str] = Query(None, alias="type"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """查询流水列表"""
    service = TransactionService(db)
    offset = (page - 1) * size
    items, total = await service.list_transactions(
        user_id=current_user.id,
        category_id=category_id,
        type_=type_,
        start_date=start_date,
        end_date=end_date,
        offset=offset,
        limit=size,
    )
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        size=size,
    )


@router.get("/{transaction_id}", response_model=TransactionOut)
async def get_transaction(
    transaction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取单条记账记录"""
    service = TransactionService(db)
    try:
        return await service.get_transaction(transaction_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{transaction_id}", response_model=TransactionOut)
async def update_transaction(
    transaction_id: int,
    payload: TransactionUpdate,
    db: AsyncSession = Depends(get_write_db),
    current_user: User = Depends(get_current_user),
):
    """更新记账记录（factory context manager 自动 commit）"""
    service = TransactionService(db)
    try:
        return await service.update_transaction(transaction_id, current_user.id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: int,
    db: AsyncSession = Depends(get_write_db),
    current_user: User = Depends(get_current_user),
):
    """软删除记账记录（factory context manager 自动 commit）"""
    service = TransactionService(db)
    try:
        await service.delete_transaction(transaction_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
