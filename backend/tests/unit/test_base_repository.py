"""BaseRepository 单元测试"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from repositories.base import BaseRepository
from infrastructure.db import Base
from sqlalchemy import Column, Integer, String


class DummyModel(Base):
    __tablename__ = "dummy"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))


class TestBaseRepository:
    @pytest.fixture
    def repo(self):
        mock_session = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()
        return BaseRepository(mock_session, DummyModel)

    @pytest.mark.asyncio
    async def test_create(self, repo):
        obj = DummyModel(name="test")
        repo.session.add = MagicMock()
        repo.session.flush = AsyncMock()

        result = await repo.create(obj)
        assert result.name == "test"
        repo.session.add.assert_called_once_with(obj)

    @pytest.mark.asyncio
    async def test_get_by_id(self, repo):
        expected = DummyModel(id=1, name="found")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=expected)
        repo.session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_by_id(1)
        assert result.name == "found"

    @pytest.mark.asyncio
    async def test_count(self, repo):
        mock_result = MagicMock()
        mock_result.scalar = MagicMock(return_value=5)
        repo.session.execute = AsyncMock(return_value=mock_result)

        result = await repo.count()
        assert result == 5

    @pytest.mark.asyncio
    async def test_delete(self, repo):
        obj = DummyModel(id=1, name="delete_me")
        repo.session.delete = AsyncMock()
        await repo.delete(obj)
        repo.session.delete.assert_called_once_with(obj)
