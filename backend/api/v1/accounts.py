"""账户管理（钱包/银行卡/支付宝/微信等）"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db, get_write_db, get_current_user
from schemas.account import AccountCreate, AccountUpdate, AccountOut
from services.account import AccountService
from models.user import User

router = APIRouter()


@router.post("", response_model=AccountOut, status_code=status.HTTP_201_CREATED)
async def create_account(
    payload: AccountCreate,
    db: AsyncSession = Depends(get_write_db),
    current_user: User = Depends(get_current_user),
):
    service = AccountService(db)
    return await service.create_account(current_user.id, payload)


@router.get("", response_model=List[AccountOut])
async def list_accounts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AccountService(db)
    return await service.list_accounts(current_user.id)


@router.get("/{account_id}", response_model=AccountOut)
async def get_account(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AccountService(db)
    account = await service.get_account(account_id, current_user.id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="账户不存在")
    return account


@router.put("/{account_id}", response_model=AccountOut)
async def update_account(
    account_id: int,
    payload: AccountUpdate,
    db: AsyncSession = Depends(get_write_db),
    current_user: User = Depends(get_current_user),
):
    service = AccountService(db)
    try:
        return await service.update_account(account_id, current_user.id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: int,
    db: AsyncSession = Depends(get_write_db),
    current_user: User = Depends(get_current_user),
):
    service = AccountService(db)
    try:
        await service.delete_account(account_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
