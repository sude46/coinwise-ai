"""UnitOfWork 单元测试"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.uow import UnitOfWork


class TestUnitOfWork:
    @pytest.mark.asyncio
    async def test_uow_initializes_repos(self):
        mock_session = MagicMock()
        with patch("services.uow.get_db_session") as mock_get_db:
            mock_cm = AsyncMock()
            mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
            mock_cm.__aexit__ = AsyncMock(return_value=None)
            mock_get_db.return_value = mock_cm

            async with UnitOfWork(for_write=True) as uow:
                assert uow.user_repo is not None
                assert uow.transaction_repo is not None
                assert uow.category_repo is not None
                assert uow.budget_repo is not None
                assert uow.report_repo is not None
