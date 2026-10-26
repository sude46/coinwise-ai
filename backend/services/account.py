from typing import Optional, List
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from models.account import Account
from repositories.account import AccountRepository
from schemas.account import AccountCreate, AccountUpdate


class AccountService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = AccountRepository(session)

    async def create_account(self, user_id: int, payload: AccountCreate) -> Account:
        account = Account(
            user_id=user_id,
            name=payload.name,
            account_type=payload.account_type,
            balance=payload.balance,
            icon=payload.icon,
            is_default=payload.is_default,
        )
        return await self.repo.create(account)

    async def list_accounts(self, user_id: int) -> List[Account]:
        return await self.repo.list_by_user(user_id)

    async def get_account(self, account_id: int, user_id: int) -> Optional[Account]:
        return await self.repo.get_by_id(account_id, user_id)

    async def get_total_balance(self, user_id: int) -> Decimal:
        return await self.repo.get_total_balance(user_id)

    async def update_account(self, account_id: int, user_id: int, payload: AccountUpdate) -> Account:
        account = await self.repo.get_by_id(account_id, user_id)
        if not account:
            raise ValueError("账户不存在")
        return await self.repo.update(account, payload.model_dump(exclude_unset=True))

    async def delete_account(self, account_id: int, user_id: int) -> None:
        account = await self.repo.get_by_id(account_id, user_id)
        if not account:
            raise ValueError("账户不存在")
        await self.repo.soft_delete(account)
