from typing import Optional, List
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.account import Account


class AccountRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, account: Account) -> Account:
        self.session.add(account)
        await self.session.flush()
        await self.session.refresh(account)
        return account

    async def get_by_id(self, account_id: int, user_id: int) -> Optional[Account]:
        result = await self.session.execute(
            select(Account).where(
                Account.id == account_id,
                Account.user_id == user_id,
                Account.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: int) -> List[Account]:
        result = await self.session.execute(
            select(Account).where(
                Account.user_id == user_id,
                Account.is_deleted == False,
            ).order_by(Account.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_total_balance(self, user_id: int) -> Decimal:
        result = await self.session.execute(
            select(func.sum(Account.balance)).where(
                Account.user_id == user_id,
                Account.is_deleted == False,
            )
        )
        return result.scalar() or 0

    async def update(self, account: Account, update_data: dict) -> Account:
        for key, value in update_data.items():
            if value is not None:
                setattr(account, key, value)
        self.session.add(account)
        return account

    async def soft_delete(self, account: Account) -> None:
        account.is_deleted = True
        self.session.add(account)
