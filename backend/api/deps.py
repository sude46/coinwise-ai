"""依赖注入：CurrentUser、DB Session、Redis"""

from typing import Optional, AsyncGenerator
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import UnauthorizedException
from infrastructure.factory import get_db_session, get_redis
from services.token import TokenService
from services.auth import AuthService
from models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI Depends 用：获取只读数据库 Session（从库）"""
    async with get_db_session(for_write=False) as session:
        yield session


async def get_write_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI Depends 用：获取可写数据库 Session（主库，自动 commit）"""
    async with get_db_session(for_write=True) as session:
        yield session


async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """JWT 校验 + 黑名单检查（Redis 不可用时跳过黑名单检查）"""
    token_service = TokenService()
    payload = token_service.decode_token(token)
    if payload is None:
        raise UnauthorizedException("无效的认证凭据")

    # 黑名单检查（Redis 不可用时优雅降级）
    jti = payload.get("jti")
    if jti:
        try:
            redis_client = await get_redis()
            is_blacklisted = await redis_client.sismember("jwt_blacklist", jti)
            if is_blacklisted:
                raise UnauthorizedException("Token 已失效")
        except Exception:
            # Redis 不可用：跳过黑名单检查，继续认证流程
            pass

    # 查询用户（需要数据库）
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(token)
    if not user:
        raise UnauthorizedException("无效的认证凭据")
    if not user.is_active:
        raise UnauthorizedException("用户已被禁用")

    # 将 user_id 写入 request.state，供审计中间件使用
    request.state.user_id = user.id
    return user


async def get_optional_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    if not token:
        return None
    try:
        return await get_current_user(request, token, db)
    except Exception:
        return None
