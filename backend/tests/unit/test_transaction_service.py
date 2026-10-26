"""TransactionService 单元测试"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal
from services.transaction import TransactionService
from schemas.transaction import TransactionCreate, TransactionUpdate


class TestTransactionService:
    @pytest.fixture
    def service(self):
        mock_session = MagicMock()
        svc = TransactionService(mock_session)
        svc.repo = MagicMock()
        svc.savings_record_repo = MagicMock()
        return svc

    @pytest.mark.asyncio
    async def test_create_transaction(self, service):
        from models.transaction import Transaction
        service.repo.create = AsyncMock(return_value=Transaction(
            id=1, user_id=1, type="expense", amount=Decimal("10"), transaction_date=datetime.now()
        ))

        data = TransactionCreate(type="expense", amount=Decimal("10"), transaction_date=datetime.now())
        with patch("services.transaction.event_bus.publish", new_callable=AsyncMock):
            result = await service.create_transaction(user_id=1, data=data)
        assert result.id == 1

    @pytest.mark.asyncio
    async def test_get_transaction_not_found(self, service):
        service.repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(ValueError, match="交易记录不存在"):
            await service.get_transaction(999, 1)

    @pytest.mark.asyncio
    async def test_get_transaction_success(self, service):
        from models.transaction import Transaction
        tx = Transaction(id=1, user_id=1, type="expense", amount=Decimal("10"), transaction_date=datetime.now())
        service.repo.get_by_id = AsyncMock(return_value=tx)

        result = await service.get_transaction(1, 1)
        assert result.id == 1

    @pytest.mark.asyncio
    async def test_delete_transaction(self, service):
        from models.transaction import Transaction
        tx = Transaction(id=1, user_id=1, type="expense", amount=Decimal("10"), transaction_date=datetime.now())
        service.repo.get_by_id = AsyncMock(return_value=tx)
        service.repo.soft_delete = AsyncMock()
        service.savings_record_repo.delete_by_transaction = AsyncMock()

        with patch("services.transaction.event_bus.publish", new_callable=AsyncMock):
            await service.delete_transaction(1, 1)
        service.repo.soft_delete.assert_called_once()
        service.savings_record_repo.delete_by_transaction.assert_called_once_with(1)
