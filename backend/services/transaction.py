from typing import Optional, List, Tuple
from datetime import datetime
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.transaction import TransactionRepository
from repositories.savings_record import SavingsRecordRepository
from models.transaction import Transaction
from models.budget import Budget
from schemas.transaction import TransactionCreate, TransactionUpdate
from events.event_bus import event_bus


class TransactionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = TransactionRepository(session)
        self.savings_record_repo = SavingsRecordRepository(session)

    async def create_transaction(self, user_id: int, data: TransactionCreate) -> Transaction:
        transaction = Transaction(
            tenant_id=0,
            user_id=user_id,
            category_id=data.category_id,
            account_id=data.account_id,
            goal_id=data.goal_id,
            type=data.type,
            amount=data.amount,
            remark=data.remark,
            source=data.source or "manual",
            transaction_date=data.transaction_date,
            created_by=user_id,
        )
        result = await self.repo.create(transaction)

        if data.goal_id:
            await self.savings_record_repo.create(
                goal_id=data.goal_id,
                transaction_id=result.id,
                amount=result.amount,
                tenant_id=0,
            )
            from repositories.savings_goal import SavingsGoalRepository
            goal_repo = SavingsGoalRepository(self.session)
            goal = await goal_repo.get_by_id(data.goal_id, user_id)
            if goal:
                new_amount = goal.current_amount + data.amount
                await goal_repo.update_current_amount(data.goal_id, user_id, new_amount)
                if new_amount >= goal.target_amount and goal.status == "active":
                    goal.status = "completed"
                    self.session.add(goal)

        if data.account_id:
            from repositories.account import AccountRepository
            acc_repo = AccountRepository(self.session)
            account = await acc_repo.get_by_id(data.account_id, user_id)
            if account:
                if data.type == "expense":
                    account.balance -= data.amount
                else:
                    account.balance += data.amount
                self.session.add(account)

        await self.session.commit()

        await event_bus.publish("transaction.created", {
            "tx_id": result.id,
            "user_id": result.user_id,
            "goal_id": result.goal_id,
            "amount": float(result.amount),
            "category_id": result.category_id,
            "remark": result.remark,
            "type": result.type,
        })
        return result

    async def get_transaction(self, transaction_id: int, user_id: int) -> Transaction:
        transaction = await self.repo.get_by_id(transaction_id, user_id)
        if not transaction:
            raise ValueError("交易记录不存在")
        return transaction

    async def list_transactions(
        self,
        user_id: int,
        category_id: Optional[int] = None,
        type_: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Transaction], int]:
        return await self.repo.list_by_user(
            user_id=user_id,
            category_id=category_id,
            type_=type_,
            start_date=start_date,
            end_date=end_date,
            offset=offset,
            limit=limit,
        )

    async def update_transaction(
        self, transaction_id: int, user_id: int, data: TransactionUpdate
    ) -> Transaction:
        transaction = await self.get_transaction(transaction_id, user_id)
        old_category_id = transaction.category_id
        old_type = transaction.type
        old_goal_id = transaction.goal_id
        old_amount = transaction.amount
        old_account_id = transaction.account_id

        update_dict = data.model_dump(exclude_unset=True)
        update_dict["updated_by"] = user_id
        result = await self.repo.update(transaction, update_dict)

        if old_account_id:
            from repositories.account import AccountRepository
            acc_repo = AccountRepository(self.session)
            account = await acc_repo.get_by_id(old_account_id, user_id)
            if account:
                if old_type == "expense":
                    account.balance += old_amount
                else:
                    account.balance -= old_amount
                self.session.add(account)

        new_account_id = getattr(result, "account_id", None)
        if new_account_id and new_account_id != old_account_id:
            from repositories.account import AccountRepository
            acc_repo = AccountRepository(self.session)
            account = await acc_repo.get_by_id(new_account_id, user_id)
            if account:
                if result.type == "expense":
                    account.balance -= result.amount
                else:
                    account.balance += result.amount
                self.session.add(account)

        if result.goal_id != old_goal_id:
            await self.savings_record_repo.delete_by_transaction(result.id)
            if result.goal_id:
                await self.savings_record_repo.create(
                    goal_id=result.goal_id,
                    transaction_id=result.id,
                    amount=result.amount,
                    tenant_id=0,
                )

        await self.session.commit()

        await event_bus.publish("transaction.updated", {
            "tx_id": result.id,
            "user_id": result.user_id,
            "goal_id": result.goal_id,
            "amount": float(result.amount),
            "category_id": result.category_id,
            "old_category_id": old_category_id,
            "remark": result.remark,
            "type": result.type,
            "old_type": old_type,
        })
        return result

    async def delete_transaction(self, transaction_id: int, user_id: int) -> None:
        transaction = await self.get_transaction(transaction_id, user_id)
        year_month = transaction.transaction_date.strftime("%Y-%m")
        await self.repo.soft_delete(transaction, deleted_by=user_id)

        if transaction.account_id:
            from repositories.account import AccountRepository
            acc_repo = AccountRepository(self.session)
            account = await acc_repo.get_by_id(transaction.account_id, user_id)
            if account:
                if transaction.type == "expense":
                    account.balance += transaction.amount
                else:
                    account.balance -= transaction.amount
                self.session.add(account)

        await self.savings_record_repo.delete_by_transaction(transaction_id)

        if transaction.goal_id:
            from repositories.savings_goal import SavingsGoalRepository
            goal_repo = SavingsGoalRepository(self.session)
            goal = await goal_repo.get_by_id(transaction.goal_id, user_id)
            if goal:
                new_amount = max(Decimal("0"), goal.current_amount - transaction.amount)
                await goal_repo.update_current_amount(transaction.goal_id, user_id, new_amount)

        await self.session.commit()

        await event_bus.publish("transaction.deleted", {
            "tx_id": transaction_id,
            "user_id": user_id,
            "goal_id": transaction.goal_id,
            "category_id": transaction.category_id,
            "type": transaction.type,
            "year_month": year_month,
        })
