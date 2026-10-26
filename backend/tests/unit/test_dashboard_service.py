"""DashboardService 单元测试"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal
from services.dashboard import DashboardService


class TestDashboardService:
    @pytest.fixture
    def service(self):
        mock_session = MagicMock()
        mock_session.execute = AsyncMock()
        return DashboardService(mock_session)

    @pytest.mark.asyncio
    async def test_get_dashboard_structure(self, service):
        # Mock 内部聚合方法
        service._get_monthly_income = AsyncMock(return_value=Decimal("10000"))
        service._get_monthly_expense = AsyncMock(return_value=Decimal("4000"))
        service._get_total_budget = AsyncMock(return_value=Decimal("5000"))
        service._get_recent_transactions = AsyncMock(return_value=[])
        service._get_category_pie = AsyncMock(return_value=[{"name": "餐饮", "value": 2000}])
        service._get_trend = AsyncMock(return_value=[{"month": "2025-01", "income": 8000, "expense": 3000}])

        # Mock AccountService 避免深层 session 调用
        with patch("services.dashboard.AccountService") as mock_acc_svc:
            mock_instance = MagicMock()
            mock_instance.get_total_balance = AsyncMock(return_value=Decimal("20000"))
            mock_acc_svc.return_value = mock_instance

            result = await service.get_dashboard(user_id=1, year_month="2025-05")

        assert result["month_income"] == 10000.0
        assert result["month_expense"] == 4000.0
        assert result["balance"] == 6000.0
        assert result["budget_remaining"] == 1000.0
        assert result["wallet_balance"] == 20000.0
        assert len(result["category_pie"]) == 1
        assert len(result["trend"]) == 1

    @pytest.mark.asyncio
    async def test_year_month_filter(self):
        from sqlalchemy import Column, DateTime
        from sqlalchemy.sql import and_

        filter_expr = DashboardService._year_month_filter(Column("dt", DateTime), "2025-05")
        assert filter_expr is not None
