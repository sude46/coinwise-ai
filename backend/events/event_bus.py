"""事件总线：发布/订阅实现"""

import asyncio
import logging
from typing import Callable, Dict, List, Any

logger = logging.getLogger(__name__)


class EventBus:
    """内存异步事件总线"""

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str):
        """订阅装饰器"""
        def decorator(func: Callable):
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(func)
            return func
        return decorator

    async def publish(self, event_type: str, payload: dict):
        """发布事件"""
        handlers = self._subscribers.get(event_type, [])
        if not handlers:
            logger.debug(f"No handlers for event {event_type}")
            return

        tasks = []
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    tasks.append(asyncio.create_task(handler(payload)))
                else:
                    handler(payload)
            except Exception as e:
                logger.error(f"Error dispatching event {event_type} to {handler}: {e}")

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


event_bus = EventBus()
