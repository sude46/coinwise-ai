"""BaseAgent 抽象基类"""

from abc import ABC, abstractmethod


class BaseAgent(ABC):
    name: str = "base"

    @abstractmethod
    async def execute(self, payload: dict) -> dict:
        """执行 Agent 逻辑，返回结构化结果"""
        pass
