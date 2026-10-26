"""FinanceStrategyAgent — 财务策略 Agent

基于用户预算、存钱计划和消费习惯，生成策略建议。
如：超支时计算对存钱计划的影响天数并给出调整建议。
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from agents.base import BaseAgent


class FinanceStrategyAgent(BaseAgent):
    """财务策略建议 Agent"""

    async def execute(self, payload: dict) -> dict:
        action = payload.get("action")
        if action == "budget_conflict":
            return self._analyze_budget_conflict(payload)
        if action == "savings_advice":
            return self._savings_advice(payload)
        return {"success": False, "error": "未知策略类型"}

    def _analyze_budget_conflict(self, payload: dict) -> dict:
        """分析预算超支对存钱计划的影响"""
        overspent = Decimal(str(payload.get("overspent", 0)))
        daily_required = Decimal(str(payload.get("daily_required", 0)))
        goal_name = payload.get("goal_name", "当前计划")

        if daily_required > 0:
            delay_days = int(overspent / daily_required)
            message = (
                f"本月超支 ¥{overspent}，"
                f"将导致「{goal_name}」延迟约 {delay_days} 天达成。"
                f"建议从下月起每日多存 ¥{daily_required * Decimal('1.2'):.1f} 以追赶进度。"
            )
        else:
            message = f"本月超支 ¥{overspent}，注意控制非必要支出。"

        return {
            "success": True,
            "type": "strategy_advice",
            "message": message,
            "delay_days": delay_days if daily_required > 0 else 0,
        }

    def _savings_advice(self, payload: dict) -> dict:
        """日常存钱建议"""
        remaining = Decimal(str(payload.get("remaining", 0)))
        days_left = payload.get("days_left", 1)
        daily = remaining / max(days_left, 1)

        return {
            "success": True,
            "type": "strategy_advice",
            "message": (
                f"距离截止还有 {days_left} 天，"
                f"建议每日存入 ¥{daily:.1f} 以按时达成目标。"
            ),
            "daily_required": float(daily),
        }
