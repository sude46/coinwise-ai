"""注册 / 登录 / 注销 / Token 刷新"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db, get_write_db, get_current_user, oauth2_scheme
from schemas.auth import UserLogin, TokenResponse, RefreshTokenRequest
from schemas.user import UserCreate, UserOut
from services.auth import AuthService
from services.token import TokenService
from models.user import User
from infrastructure.factory import get_redis

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserCreate,
    db: AsyncSession = Depends(get_write_db),
):
    """用户注册（factory context manager 自动 commit）"""
    auth_service = AuthService(db)
    try:
        return await auth_service.register(
            username=payload.username,
            email=payload.email,
            password=payload.password,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: UserLogin,
    db: AsyncSession = Depends(get_write_db),
):
    """用户登录"""
    auth_service = AuthService(db)
    user = await auth_service.authenticate(payload.username, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    access_token = auth_service.create_access_token(user.id)
    refresh_token = auth_service.create_refresh_token(user.id)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
):
    auth_service = TokenService()
    payload = auth_service.decode_token(token)
    if payload and "jti" in payload:
        redis_client = await get_redis()
        await redis_client.sadd("jwt_blacklist", payload["jti"])
        await redis_client.expire("jwt_blacklist", 7 * 24 * 3600)  # 7天过期
    return {"message": "注销成功"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """刷新 Access Token"""
    auth_service = AuthService(db)
    payload_data = auth_service.decode_token(payload.refresh_token)
    if not payload_data or payload_data.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌",
        )
    user_id = int(payload_data.get("sub"))
    user = await auth_service.user_repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用",
        )
    access_token = auth_service.create_access_token(user.id)
    refresh_token = auth_service.create_refresh_token(user.id)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )
