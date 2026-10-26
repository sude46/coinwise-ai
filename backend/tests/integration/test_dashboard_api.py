"""仪表盘接口集成测试"""

import pytest
from datetime import datetime


class TestDashboardAPI:
    @pytest.fixture
    def auth_headers(self, client):
        client.post("/api/v1/auth/register", json={
            "username": "dash_user",
            "email": "dash@example.com",
            "password": "123456",
        })
        r = client.post("/api/v1/auth/login", json={
            "username": "dash_user",
            "password": "123456",
        })
        token = r.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_dashboard_structure(self, client, auth_headers):
        # 创建一些交易数据
        for i in range(3):
            client.post("/api/v1/transactions", json={
                "type": "expense",
                "amount": 100 + i * 10,
                "transaction_date": datetime.now().isoformat(),
            }, headers=auth_headers)
        client.post("/api/v1/transactions", json={
            "type": "income",
            "amount": 5000,
            "transaction_date": datetime.now().isoformat(),
        }, headers=auth_headers)

        r = client.get("/api/v1/dashboard", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "month_income" in data
        assert "month_expense" in data
        assert "balance" in data
        assert "budget_remaining" in data
        assert "recent_transactions" in data
        assert "category_pie" in data
        assert "trend" in data
        assert len(data["trend"]) == 6  # 近6个月

    def test_dashboard_unauthorized(self, client):
        r = client.get("/api/v1/dashboard")
        assert r.status_code == 401
