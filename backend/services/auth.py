from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from repositories.user import UserRepository
from models.user import User
from services.token import TokenService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """认证业务服务：负责用户注册、密码校验、Token 签发"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.token_service = TokenService()

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    async def register(self, username: str, email: str, password: str) -> User:
        existing = await self.user_repo.get_by_username(username)
        if existing:
            raise ValueError("用户名已存在")
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise ValueError("邮箱已被注册")
        user = User(
            username=username,
            email=email,
            hashed_password=self.hash_password(password),
        )
        user = await self.user_repo.create(user)
        # 自动创建默认收支分类
        await self._init_default_categories(user.id)
        return user

    async def _init_default_categories(self, user_id: int) -> None:
        from models.category import Category
        defaults = [
            ("餐饮", "🍔"), ("交通", "🚗"), ("购物", "🛍️"), ("住房", "🏠"),
            ("娱乐", "🎮"), ("医疗", "💊"), ("教育", "📚"), ("其他", "📦"),
            ("工资", "💰"), ("奖金", "🎁"), ("理财", "📈"),
        ]
        for name, icon in defaults:
            cat = Category(user_id=user_id, name=name, icon=icon)
            self.session.add(cat)
        await self.session.flush()

    async def authenticate(self, username: str, password: str) -> Optional[User]:
        # 支持用户名或邮箱登录
        user = await self.user_repo.get_by_username(username)
        if not user:
            user = await self.user_repo.get_by_email(username)
        if not user or user.is_active is False:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    def create_access_token(self, user_id: int) -> str:
        return self.token_service.create_access_token(user_id)

    def create_refresh_token(self, user_id: int) -> str:
        return self.token_service.create_refresh_token(user_id)

    def decode_token(self, token: str) -> Optional[dict]:
        return self.token_service.decode_token(token)

    async def get_current_user(self, token: str) -> Optional[User]:
        payload = self.decode_token(token)
        if payload is None or payload.get("type") != "access":
            return None
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return await self.user_repo.get_by_id(int(user_id))
