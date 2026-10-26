"""EventBus 单元测试"""

import pytest
from events.event_bus import EventBus


class TestEventBus:
    @pytest.mark.asyncio
    async def test_subscribe_and_publish(self):
        bus = EventBus()
        received = []

        @bus.subscribe("test.event")
        async def handler(event):
            received.append(event)

        await bus.publish("test.event", {"msg": "hello"})
        assert len(received) == 1
        assert received[0]["msg"] == "hello"

    @pytest.mark.asyncio
    async def test_publish_no_handlers(self):
        bus = EventBus()
        # 不应抛出异常
        await bus.publish("no.handler", {})

    @pytest.mark.asyncio
    async def test_multiple_handlers(self):
        bus = EventBus()
        results = []

        @bus.subscribe("multi")
        async def handler1(event):
            results.append("h1")

        @bus.subscribe("multi")
        async def handler2(event):
            results.append("h2")

        await bus.publish("multi", {})
        assert sorted(results) == ["h1", "h2"]

    @pytest.mark.asyncio
    async def test_sync_handler(self):
        bus = EventBus()
        received = []

        @bus.subscribe("sync")
        def handler(event):
            received.append(event)

        await bus.publish("sync", {"data": 1})
        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_handler_exception_not_blocking(self):
        bus = EventBus()
        received = []

        @bus.subscribe("error")
        async def bad_handler(event):
            raise ValueError("boom")

        @bus.subscribe("error")
        async def good_handler(event):
            received.append(event)

        # 不应抛出异常，好 handler 仍能执行
        await bus.publish("error", {"ok": True})
        assert len(received) == 1
