"""记账接口集成测试"""

import pytest
from datetime import datetime


class TestTransactionAPI:
    @pytest.fixture
    def auth_headers(self, client):
        client.post("/api/v1/auth/register", json={
            "username": "tx_user",
            "email": "tx@example.com",
            "password": "123456",
        })
        r = client.post("/api/v1/auth/login", json={
            "username": "tx_user",
            "password": "123456",
        })
        token = r.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_create_transaction(self, client, auth_headers):
        r = client.post("/api/v1/transactions", json={
            "type": "expense",
            "amount": 35.00,
            "transaction_date": datetime.now().isoformat(),
            "remark": "星巴克咖啡",
        }, headers=auth_headers)
        assert r.status_code == 201
        data = r.json()
        assert data["type"] == "expense"
        assert float(data["amount"]) == 35.00
        assert "id" in data

    def test_create_transaction_invalid_type(self, client, auth_headers):
        r = client.post("/api/v1/transactions", json={
            "type": "invalid",
            "amount": 35.00,
            "transaction_date": datetime.now().isoformat(),
        }, headers=auth_headers)
        assert r.status_code == 422  # Pydantic validation error

    def test_create_transaction_negative_amount(self, client, auth_headers):
        r = client.post("/api/v1/transactions", json={
            "type": "expense",
            "amount": -10,
            "transaction_date": datetime.now().isoformat(),
        }, headers=auth_headers)
        assert r.status_code == 422

    def test_list_transactions(self, client, auth_headers):
        # 创建两条记录
        client.post("/api/v1/transactions", json={
            "type": "expense", "amount": 10, "transaction_date": datetime.now().isoformat(),
        }, headers=auth_headers)
        client.post("/api/v1/transactions", json={
            "type": "income", "amount": 100, "transaction_date": datetime.now().isoformat(),
        }, headers=auth_headers)

        r = client.get("/api/v1/transactions", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 2
        assert len(data["items"]) >= 2

    def test_list_transactions_with_filter(self, client, auth_headers):
        client.post("/api/v1/transactions", json={
            "type": "expense", "amount": 20, "transaction_date": datetime.now().isoformat(),
        }, headers=auth_headers)

        r = client.get("/api/v1/transactions?type=expense", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        for item in data["items"]:
            assert item["type"] == "expense"

    def test_get_transaction(self, client, auth_headers):
        create_r = client.post("/api/v1/transactions", json={
            "type": "expense", "amount": 50, "transaction_date": datetime.now().isoformat(),
        }, headers=auth_headers)
        tx_id = create_r.json()["id"]

        r = client.get(f"/api/v1/transactions/{tx_id}", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["amount"] == "50.00"

    def test_get_transaction_not_found(self, client, auth_headers):
        r = client.get("/api/v1/transactions/99999", headers=auth_headers)
        assert r.status_code == 404

    def test_update_transaction(self, client, auth_headers):
        create_r = client.post("/api/v1/transactions", json={
            "type": "expense", "amount": 10, "transaction_date": datetime.now().isoformat(),
        }, headers=auth_headers)
        tx_id = create_r.json()["id"]

        r = client.put(f"/api/v1/transactions/{tx_id}", json={
            "amount": 99.99,
            "remark": "更新后的备注",
        }, headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert float(data["amount"]) == 99.99
        assert data["remark"] == "更新后的备注"

    def test_delete_transaction(self, client, auth_headers):
        create_r = client.post("/api/v1/transactions", json={
            "type": "expense", "amount": 5, "transaction_date": datetime.now().isoformat(),
        }, headers=auth_headers)
        tx_id = create_r.json()["id"]

        r = client.delete(f"/api/v1/transactions/{tx_id}", headers=auth_headers)
        assert r.status_code == 204

        # 删除后应 404
        r2 = client.get(f"/api/v1/transactions/{tx_id}", headers=auth_headers)
        assert r2.status_code == 404

    def test_unauthorized_access(self, client):
        r = client.get("/api/v1/transactions")
        assert r.status_code == 401
