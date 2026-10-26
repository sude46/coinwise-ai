"""报告接口集成测试"""

import pytest
from datetime import datetime


class TestReportsAPI:
    @pytest.fixture
    def auth_headers(self, client):
        client.post("/api/v1/auth/register", json={
            "username": "report_user",
            "email": "report@example.com",
            "password": "123456",
        })
        r = client.post("/api/v1/auth/login", json={
            "username": "report_user",
            "password": "123456",
        })
        token = r.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_get_report(self, client, auth_headers):
        # 创建交易记录
        client.post("/api/v1/transactions", json={
            "type": "income", "amount": 8000,
            "transaction_date": datetime.now().isoformat(),
        }, headers=auth_headers)
        client.post("/api/v1/transactions", json={
            "type": "expense", "amount": 3000,
            "transaction_date": datetime.now().isoformat(),
        }, headers=auth_headers)

        year_month = datetime.now().strftime("%Y-%m")
        r = client.get(f"/api/v1/reports/{year_month}", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert data["year_month"] == year_month
        assert float(data["total_income"]) == 8000.0
        assert float(data["total_expense"]) == 3000.0
        assert float(data["balance"]) == 5000.0

    def test_list_reports(self, client, auth_headers):
        year_month = datetime.now().strftime("%Y-%m")
        client.get(f"/api/v1/reports/{year_month}", headers=auth_headers)

        r = client.get("/api/v1/reports", headers=auth_headers)
        assert r.status_code == 200
        assert len(r.json()) >= 1

    def test_reports_unauthorized(self, client):
        r = client.get("/api/v1/reports/2025-01")
        assert r.status_code == 401
