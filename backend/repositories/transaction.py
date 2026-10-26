from typing import Optional, List, Tuple
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.transaction import Transaction
from infrastructure.crypto import crypto


class TransactionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self._crypto = crypto

    def _encrypt(self, value: Optional[str]) -> Optional[str]:
        return self._crypto.encrypt(value) if value else value

    def _decrypt(self, value: Optional[str]) -> Optional[str]:
        return self._crypto.decrypt(value) if value else value

    def _decrypt_model(self, tx: Transaction) -> Transaction:
        if tx.remark:
            tx.remark = self._decrypt(tx.remark)
        return tx

    async def create(self, transaction: Transaction) -> Transaction:
        # 写入前加密敏感字段
        if transaction.remark:
            transaction.remark = self._encrypt(transaction.remark)
        self.session.add(transaction)
        await self.session.flush()
        await self.session.refresh(transaction)
        return self._decrypt_model(transaction)

    async def get_by_id(self, transaction_id: int, user_id: int) -> Optional[Transaction]:
        result = await self.session.execute(
            select(Transaction).where(
                Transaction.id == transaction_id,
                Transaction.user_id == user_id,
                Transaction.is_deleted == False,
            )
        )
        tx = result.scalar_one_or_none()
        return self._decrypt_model(tx) if tx else None

    async def list_by_user(
        self,
        user_id: int,
        category_id: Optional[int] = None,
        type_: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Transaction], int]:
        conditions = [Transaction.user_id == user_id, Transaction.is_deleted == False]
        if category_id is not None:
            conditions.append(Transaction.category_id == category_id)
        if type_ is not None:
            conditions.append(Transaction.type == type_)
        if start_date is not None:
            conditions.append(Transaction.transaction_date >= start_date)
        if end_date is not None:
            conditions.append(Transaction.transaction_date <= end_date)

        count_query = select(func.count(Transaction.id)).where(*conditions)
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()

        query = (
            select(Transaction)
            .where(*conditions)
            .order_by(Transaction.transaction_date.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(query)
        rows = result.scalars().all()
        return [self._decrypt_model(r) for r in rows], total

    async def update(self, transaction: Transaction, update_data: dict) -> Transaction:
        for key, value in update_data.items():
            if value is not None or key in ("remark", "note"):
                if key == "remark" and value is not None:
                    value = self._encrypt(value)
                setattr(transaction, key, value)
        self.session.add(transaction)
        await self.session.flush()
        return self._decrypt_model(transaction)

    async def soft_delete(self, transaction: Transaction, deleted_by: Optional[int] = None) -> None:
        transaction.is_deleted = True
        transaction.deleted_at = datetime.now()
        transaction.deleted_by = deleted_by
        self.session.add(transaction)
        await self.session.flush()
