"""异常路径集成测试"""

import pytest
from datetime import datetime


class TestExceptionPaths:
    @pytest.fixture
    def auth_headers(self, client):
        client.post("/api/v1/auth/register", json={
            "username": "ex_user",
            "email": "ex@example.com",
            "password": "123456",
        })
        r = client.post("/api/v1/auth/login", json={
            "username": "ex_user",
            "password": "123456",
        })
        token = r.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    # 400 Bad Request
    def test_budget_invalid_year_month_format(self, client, auth_headers):
        r = client.post("/api/v1/budgets", json={
            "year_month": "invalid",
            "limit_amount": 1000,
        }, headers=auth_headers)
        assert r.status_code == 422

    # 404 Not Found
    def test_get_nonexistent_transaction(self, client, auth_headers):
        r = client.get("/api/v1/transactions/99999", headers=auth_headers)
        assert r.status_code == 404

    def test_get_nonexistent_budget(self, client, auth_headers):
        r = client.get("/api/v1/budgets/99999", headers=auth_headers)
        assert r.status_code == 404

    def test_update_nonexistent_transaction(self, client, auth_headers):
        r = client.put("/api/v1/transactions/99999", json={
            "amount": 100,
        }, headers=auth_headers)
        assert r.status_code == 404

    # 422 Validation Error
    def test_transaction_invalid_amount(self, client, auth_headers):
        r = client.post("/api/v1/transactions", json={
            "type": "expense",
            "amount": 0,
            "transaction_date": datetime.now().isoformat(),
        }, headers=auth_headers)
        assert r.status_code == 422

    def test_register_invalid_email(self, client):
        r = client.post("/api/v1/auth/register", json={
            "username": "user",
            "email": "not-an-email",
            "password": "123456",
        })
        assert r.status_code == 422

    def test_register_short_password(self, client):
        r = client.post("/api/v1/auth/register", json={
            "username": "user2",
            "email": "user2@example.com",
            "password": "123",
        })
        # password 没有长度限制，所以应该是 201
        assert r.status_code == 201

    # 401 Unauthorized
    def test_access_protected_without_token(self, client):
        r = client.get("/api/v1/dashboard")
        assert r.status_code == 401

    def test_access_with_invalid_token(self, client):
        r = client.get("/api/v1/dashboard", headers={"Authorization": "Bearer invalid_token"})
        assert r.status_code == 401
