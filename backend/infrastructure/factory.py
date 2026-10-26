"""工厂模式：统一创建所有基础设施客户端，支持单例/连接池复用"""

from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.db import async_session_master, async_session_slave
import redis.asyncio as redis
from core.config import settings

# ── 单例缓存 ──
_redis_pool: Optional[redis.Redis] = None
_es_client: Optional[object] = None


@asynccontextmanager
async def get_db_session(for_write: bool = False) -> AsyncGenerator[AsyncSession, None]:
    """获取 SQLAlchemy AsyncSession（自动 commit/rollback/close）"""
    session_maker = async_session_master if for_write else async_session_slave
    async with session_maker() as session:
        try:
            yield session
            if for_write:
                await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_redis() -> redis.Redis:
    """获取 Redis 客户端（单例连接池）"""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            max_connections=50,
        )
    return _redis_pool


async def close_redis():
    """关闭 Redis 连接池（应用退出时调用）"""
    global _redis_pool
    if _redis_pool is not None:
        try:
            await _redis_pool.aclose()
        except Exception:
            _redis_pool = None


async def get_es() -> object:
    """获取 Elasticsearch 客户端（单例，可选组件，默认关闭）

    文档明确建议删除 ES（过度设计），保留接口但默认不初始化。
    如需启用，设置 ES_ENABLED=true 并安装 elasticsearch 包。
    """
    global _es_client
    if _es_client is None and getattr(settings, "ES_ENABLED", False):
        from elasticsearch import AsyncElasticsearch
        _es_client = AsyncElasticsearch(
            hosts=[settings.ES_HOST],
            request_timeout=30,
        )
    if _es_client is None:
        raise RuntimeError("Elasticsearch is disabled. Use MySQL FULLTEXT instead.")
    return _es_client


def get_celery():
    """获取 Celery 应用实例（单例，复用 tasks.celery_app 中的实例）"""
    from tasks.celery_app import celery_app
    return celery_app
