"""通用 CRUD、读写分离路由基类"""

from typing import TypeVar, Generic, Optional, List, Type
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db import Base
from infrastructure.crypto import crypto

ModelType = TypeVar("ModelType", bound=Base)


# 需要加密的字段映射：{模型类名: [字段名列表]}
_ENCRYPTED_FIELDS = {
    "Transaction": ["remark"],
    "SavingsGoal": ["name", "note"],
}


class BaseRepository(Generic[ModelType]):
    """
    通用 Repository 基类
    封装基础 CRUD 操作，支持读写分离路由
    自动加解密敏感字段（在 _ENCRYPTED_FIELDS 中注册）
    """

    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self.session = session
        self.model = model
        self._crypto = crypto
        self._encrypted_fields = _ENCRYPTED_FIELDS.get(model.__name__, [])

    def _encrypt_field(self, value: Optional[str]) -> Optional[str]:
        return self._crypto.encrypt(value) if value else value

    def _decrypt_field(self, value: Optional[str]) -> Optional[str]:
        return self._crypto.decrypt(value) if value else value

    def _encrypt_dict(self, data: dict) -> dict:
        """对字典中的敏感字段进行加密（用于 create/update 前）"""
        result = dict(data)
        for field in self._encrypted_fields:
            if field in result and result[field] is not None:
                result[field] = self._encrypt_field(result[field])
        return result

    def _decrypt_model(self, obj: ModelType) -> ModelType:
        """对模型实例的敏感字段进行解密（读取后）"""
        for field in self._encrypted_fields:
            if hasattr(obj, field):
                raw = getattr(obj, field)
                if raw is not None:
                    setattr(obj, field, self._decrypt_field(raw))
        return obj

    async def create(self, obj: ModelType) -> ModelType:
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return self._decrypt_model(obj)

    async def get_by_id(self, obj_id: int) -> Optional[ModelType]:
        result = await self.session.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        obj = result.scalar_one_or_none()
        return self._decrypt_model(obj) if obj else None

    async def list_all(self, offset: int = 0, limit: int = 100) -> List[ModelType]:
        result = await self.session.execute(
            select(self.model).offset(offset).limit(limit)
        )
        rows = result.scalars().all()
        return [self._decrypt_model(r) for r in rows]

    async def count(self) -> int:
        result = await self.session.execute(select(func.count(self.model.id)))
        return result.scalar() or 0

    async def delete(self, obj: ModelType) -> None:
        await self.session.delete(obj)
