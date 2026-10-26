"""TokenService 单元测试（纯计算，无需数据库）"""

import pytest
from jose import jwt
from services.token import TokenService
from core.config import settings


class TestTokenService:
    def test_create_and_decode_access_token(self):
        token = TokenService.create_access_token(user_id=1)
        payload = TokenService.decode_token(token)

        assert payload is not None
        assert payload["sub"] == "1"
        assert payload["type"] == "access"
        assert "jti" in payload
        assert "exp" in payload

    def test_create_and_decode_refresh_token(self):
        token = TokenService.create_refresh_token(user_id=42)
        payload = TokenService.decode_token(token)

        assert payload is not None
        assert payload["sub"] == "42"
        assert payload["type"] == "refresh"

    def test_decode_invalid_token(self):
        payload = TokenService.decode_token("invalid.token.here")
        assert payload is None

    def test_token_signature_verification(self):
        token = TokenService.create_access_token(user_id=1)
        # 用正确密钥验证
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        assert payload["sub"] == "1"

    def test_access_and_refresh_are_different(self):
        access = TokenService.create_access_token(user_id=1)
        refresh = TokenService.create_refresh_token(user_id=1)
        assert access != refresh
