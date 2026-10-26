"""预算接口集成测试"""

import pytest


class TestBudgetAPI:
    @pytest.fixture
    def auth_headers(self, client):
        client.post("/api/v1/auth/register", json={
            "username": "budget_user",
            "email": "budget@example.com",
            "password": "123456",
        })
        r = client.post("/api/v1/auth/login", json={
            "username": "budget_user",
            "password": "123456",
        })
        token = r.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_create_budget(self, client, auth_headers):
        r = client.post("/api/v1/budgets", json={
            "year_month": "2025-05",
            "limit_amount": 3000.00,
        }, headers=auth_headers)
        assert r.status_code == 201
        data = r.json()
        assert data["year_month"] == "2025-05"
        assert float(data["limit_amount"]) == 3000.00

    def test_create_duplicate_budget(self, client, auth_headers):
        client.post("/api/v1/budgets", json={
            "year_month": "2025-06",
            "limit_amount": 2000,
        }, headers=auth_headers)
        r = client.post("/api/v1/budgets", json={
            "year_month": "2025-06",
            "limit_amount": 2500,
        }, headers=auth_headers)
        assert r.status_code == 400
        assert "预算已存在" in r.json()["detail"]

    def test_list_budgets(self, client, auth_headers):
        client.post("/api/v1/budgets", json={
            "year_month": "2025-07",
            "limit_amount": 1500,
        }, headers=auth_headers)
        r = client.get("/api/v1/budgets", headers=auth_headers)
        assert r.status_code == 200
        assert len(r.json()) >= 1

    def test_get_budget(self, client, auth_headers):
        create_r = client.post("/api/v1/budgets", json={
            "year_month": "2025-08",
            "limit_amount": 5000,
        }, headers=auth_headers)
        budget_id = create_r.json()["id"]
        r = client.get(f"/api/v1/budgets/{budget_id}", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["limit_amount"] == "5000.00"

    def test_update_budget(self, client, auth_headers):
        create_r = client.post("/api/v1/budgets", json={
            "year_month": "2025-09",
            "limit_amount": 1000,
        }, headers=auth_headers)
        budget_id = create_r.json()["id"]
        r = client.put(f"/api/v1/budgets/{budget_id}", json={
            "year_month": "2025-09",
            "limit_amount": 2000,
        }, headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["limit_amount"] == "2000"

    def test_delete_budget(self, client, auth_headers):
        create_r = client.post("/api/v1/budgets", json={
            "year_month": "2025-10",
            "limit_amount": 800,
        }, headers=auth_headers)
        budget_id = create_r.json()["id"]
        r = client.delete(f"/api/v1/budgets/{budget_id}", headers=auth_headers)
        assert r.status_code == 204

    def test_unauthorized(self, client):
        r = client.get("/api/v1/budgets")
        assert r.status_code == 401
