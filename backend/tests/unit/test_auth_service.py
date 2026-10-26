"""AuthService 单元测试（使用 mock 的 Repository）"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from services.auth import AuthService
from models.user import User


class TestAuthService:
    @pytest.fixture
    def auth_service(self):
        mock_session = MagicMock()
        mock_session.execute = AsyncMock()
        mock_session.flush = AsyncMock()
        return AuthService(mock_session)

    @pytest.mark.asyncio
    async def test_hash_and_verify_password(self, auth_service):
        hashed = auth_service.hash_password("secret123")
        assert hashed != "secret123"
        assert auth_service.verify_password("secret123", hashed) is True
        assert auth_service.verify_password("wrong", hashed) is False

    @pytest.mark.asyncio
    async def test_register_success(self, auth_service):
        auth_service.user_repo.get_by_username = AsyncMock(return_value=None)
        auth_service.user_repo.get_by_email = AsyncMock(return_value=None)
        auth_service.user_repo.create = AsyncMock(return_value=User(
            id=1, username="alice", email="alice@example.com", hashed_password="xxx"
        ))

        user = await auth_service.register("alice", "alice@example.com", "password")
        assert user.username == "alice"

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, auth_service):
        auth_service.user_repo.get_by_username = AsyncMock(return_value=User(id=1))

        with pytest.raises(ValueError, match="用户名已存在"):
            await auth_service.register("alice", "alice@example.com", "password")

    @pytest.mark.asyncio
    async def test_authenticate_success(self, auth_service):
        hashed = auth_service.hash_password("secret123")
        auth_service.user_repo.get_by_username = AsyncMock(return_value=User(
            id=1, username="alice", email="a@b.com", hashed_password=hashed
        ))

        user = await auth_service.authenticate("alice", "secret123")
        assert user is not None
        assert user.id == 1

    @pytest.mark.asyncio
    async def test_authenticate_wrong_password(self, auth_service):
        # 使用一个有效的 bcrypt hash（密码是 "correct"）
        valid_hash = auth_service.hash_password("correct")
        auth_service.user_repo.get_by_username = AsyncMock(return_value=User(
            id=1, username="alice", email="a@b.com", hashed_password=valid_hash
        ))

        user = await auth_service.authenticate("alice", "secret123")
        assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, auth_service):
        auth_service.user_repo.get_by_username = AsyncMock(return_value=None)
        auth_service.user_repo.get_by_email = AsyncMock(return_value=None)

        user = await auth_service.authenticate("nobody", "secret123")
        assert user is None
