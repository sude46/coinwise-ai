"""Agent 插件单元测试（纯规则引擎，无需数据库）"""

import pytest
from agents.classify_agent import SmartCategoryAgent
from agents.alert_agent import BudgetAlertAgent
from agents.report_agent import MonthlyReportAgent


class TestSmartCategoryAgent:
    @pytest.mark.asyncio
    async def test_classify_food(self):
        agent = SmartCategoryAgent()
        result = await agent.execute({"transaction_id": 1, "remark": "星巴克咖啡"})
        assert result["suggested_category"] == "餐饮"
        assert result["confidence"] == 0.85

    @pytest.mark.asyncio
    async def test_classify_transport(self):
        agent = SmartCategoryAgent()
        result = await agent.execute({"transaction_id": 2, "remark": "地铁充值"})
        assert result["suggested_category"] == "交通"

    @pytest.mark.asyncio
    async def test_classify_other(self):
        agent = SmartCategoryAgent()
        result = await agent.execute({"transaction_id": 3, "remark": "某某未知消费"})
        assert result["suggested_category"] == "其他"


class TestBudgetAlertAgent:
    @pytest.mark.asyncio
    async def test_budget_normal(self):
        agent = BudgetAlertAgent()
        result = await agent.execute({
            "user_id": 1,
            "category_name": "餐饮",
            "limit_amount": 1000,
            "total_spent": 500,
        })
        assert result["exceeded"] is False
        assert result["warning_level"] == "normal"
        assert result["percentage"] == 50.0

    @pytest.mark.asyncio
    async def test_budget_warning(self):
        agent = BudgetAlertAgent()
        result = await agent.execute({
            "category_name": "餐饮",
            "limit_amount": 1000,
            "total_spent": 850,
        })
        assert result["exceeded"] is False
        assert result["warning_level"] == "warning"

    @pytest.mark.asyncio
    async def test_budget_danger(self):
        agent = BudgetAlertAgent()
        result = await agent.execute({
            "category_name": "餐饮",
            "limit_amount": 1000,
            "total_spent": 1200,
        })
        assert result["exceeded"] is True
        assert result["warning_level"] == "danger"


class TestMonthlyReportAgent:
    @pytest.mark.asyncio
    async def test_report_generation(self):
        agent = MonthlyReportAgent()
        result = await agent.execute({
            "user_id": 1,
            "year_month": "2025-05",
            "total_income": 10000,
            "total_expense": 4000,
            "balance": 6000,
            "category_breakdown": [
                {"name": "餐饮", "amount": 2000},
                {"name": "交通", "amount": 1000},
            ],
        })
        assert result["total_income"] == 10000.0
        assert result["balance"] == 6000.0
        assert "餐饮" in result["analysis"]
        assert result["top_expense_category"]["name"] == "餐饮"
