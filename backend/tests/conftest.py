"""测试配置和通用 Fixture"""

import pytest
import pytest_asyncio
from unittest.mock import MagicMock
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from infrastructure.db import Base
from main import app
from api.deps import get_db, get_write_db

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# ── 全局 mock Celery，避免测试环境尝试连接 Redis ──
import tasks
tasks.celery_app.send_task = MagicMock()

import tasks.transaction_tasks
tasks.transaction_tasks.sync_transaction_to_es.delay = MagicMock()

import tasks.budget_tasks
tasks.budget_tasks.check_budget_alert.delay = MagicMock()

import tasks.agent_tasks
tasks.agent_tasks.run_agent_task.delay = MagicMock()

import tasks.reconciliation_tasks
tasks.reconciliation_tasks.reconcile_goal_amount.delay = MagicMock()

import tasks.audit_tasks
tasks.audit_tasks.write_audit_log.delay = MagicMock()


@pytest_asyncio.fixture(scope="session")
async def db_engine():
    """创建测试数据库引擎（Session 级别，所有测试共享同一连接）"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    """每个测试函数独立的 Session"""
    async_session = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.commit()


@pytest.fixture
def client(db_engine):
    """同步 TestClient（手动注入测试数据库）"""
    async def override_get_db():
        async_session = async_sessionmaker(
            db_engine, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session() as session:
            yield session
            # 关键：读 session 也 commit，避免关闭时 ROLLBACK 影响共享连接上的写事务
            await session.commit()

    async def override_get_write_db():
        async_session = async_sessionmaker(
            db_engine, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session() as session:
            yield session
            await session.commit()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_write_db] = override_get_write_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
