"""Token 编解码服务（纯计算，不依赖数据库）"""

from datetime import datetime, timedelta
from typing import Optional
import uuid
from jose import JWTError, jwt
from core.config import settings


class TokenService:
    """JWT Token 的生成与解析，完全不依赖数据库 Session"""

    @staticmethod
    def create_access_token(user_id: int) -> str:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        jti = str(uuid.uuid4())
        payload = {"sub": str(user_id), "exp": expire, "type": "access", "jti": jti}
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        jti = str(uuid.uuid4())
        payload = {"sub": str(user_id), "exp": expire, "type": "refresh", "jti": jti}
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except JWTError:
            return None
