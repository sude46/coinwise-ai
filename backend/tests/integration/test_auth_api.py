"""认证接口集成测试"""

import pytest


class TestAuthAPI:
    def test_register_success(self, client):
        r = client.post("/api/v1/auth/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "123456",
        })
        assert r.status_code == 201
        data = r.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "id" in data

    def test_register_duplicate_username(self, client):
        # 先注册一个
        client.post("/api/v1/auth/register", json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "123456",
        })
        # 再注册同名
        r = client.post("/api/v1/auth/register", json={
            "username": "alice",
            "email": "alice2@example.com",
            "password": "123456",
        })
        assert r.status_code == 400
        assert "用户名已存在" in r.json()["detail"]

    def test_register_duplicate_email(self, client):
        client.post("/api/v1/auth/register", json={
            "username": "bob",
            "email": "bob@example.com",
            "password": "123456",
        })
        r = client.post("/api/v1/auth/register", json={
            "username": "bob2",
            "email": "bob@example.com",
            "password": "123456",
        })
        assert r.status_code == 400
        assert "邮箱已被注册" in r.json()["detail"]

    def test_login_success(self, client):
        client.post("/api/v1/auth/register", json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "secret123",
        })
        r = client.post("/api/v1/auth/login", json={
            "username": "loginuser",
            "password": "secret123",
        })
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        client.post("/api/v1/auth/register", json={
            "username": "wrongpass",
            "email": "wrong@example.com",
            "password": "secret123",
        })
        r = client.post("/api/v1/auth/login", json={
            "username": "wrongpass",
            "password": "wrongpassword",
        })
        assert r.status_code == 401
        assert "用户名或密码错误" in r.json()["detail"]

    def test_login_user_not_found(self, client):
        r = client.post("/api/v1/auth/login", json={
            "username": "nonexistent",
            "password": "whatever",
        })
        assert r.status_code == 401

    def test_refresh_token(self, client):
        client.post("/api/v1/auth/register", json={
            "username": "refreshuser",
            "email": "refresh@example.com",
            "password": "secret123",
        })
        login_r = client.post("/api/v1/auth/login", json={
            "username": "refreshuser",
            "password": "secret123",
        })
        refresh_token = login_r.json()["refresh_token"]

        r = client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token,
        })
        assert r.status_code == 200
        assert "access_token" in r.json()

    def test_refresh_invalid_token(self, client):
        r = client.post("/api/v1/auth/refresh", json={
            "refresh_token": "invalid.token.here",
        })
        assert r.status_code == 401
