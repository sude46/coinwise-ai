"""分类接口集成测试"""

import pytest


class TestCategoryAPI:
    @pytest.fixture
    def auth_headers(self, client):
        # 注册并登录
        client.post("/api/v1/auth/register", json={
            "username": "cat_user",
            "email": "cat@example.com",
            "password": "123456",
        })
        r = client.post("/api/v1/auth/login", json={
            "username": "cat_user",
            "password": "123456",
        })
        token = r.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_create_category(self, client, auth_headers):
        r = client.post("/api/v1/categories", json={
            "name": "餐饮",
            "icon": "food",
        }, headers=auth_headers)
        assert r.status_code == 201
        data = r.json()
        assert data["name"] == "餐饮"
        assert data["icon"] == "food"

    def test_list_categories(self, client, auth_headers):
        client.post("/api/v1/categories", json={"name": "交通"}, headers=auth_headers)
        client.post("/api/v1/categories", json={"name": "购物"}, headers=auth_headers)
        r = client.get("/api/v1/categories", headers=auth_headers)
        assert r.status_code == 200
        assert len(r.json()) >= 2

    def test_delete_category(self, client, auth_headers):
        create_r = client.post("/api/v1/categories", json={"name": "临时分类"}, headers=auth_headers)
        cat_id = create_r.json()["id"]
        r = client.delete(f"/api/v1/categories/{cat_id}", headers=auth_headers)
        assert r.status_code == 204

    def test_unauthorized_access(self, client):
        r = client.get("/api/v1/categories")
        assert r.status_code == 401

    def test_create_category_without_auth(self, client):
        r = client.post("/api/v1/categories", json={"name": "餐饮"})
        assert r.status_code == 401
