"""AnomalyAgent — 异常消费识别 Agent

检测深夜大额消费、单日同类消费超均值 3 倍等异常模式。
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any

from agents.base import BaseAgent


class AnomalyAgent(BaseAgent):
    """异常消费识别 Agent"""

    async def execute(self, payload: dict) -> dict:
        transactions = payload.get("transactions", [])
        alerts = []

        alerts.extend(self._detect_late_night_large(transactions))
        alerts.extend(self._detect_category_spike(transactions))

        return {
            "success": True,
            "type": "anomaly_report",
            "alerts": alerts,
            "has_anomaly": len(alerts) > 0,
        }

    def _detect_late_night_large(self, transactions: List[Dict[str, Any]]) -> List[dict]:
        """检测深夜（23:00-05:00）大额消费（>500）"""
        alerts = []
        for tx in transactions:
            tx_date = tx.get("transaction_date")
            if isinstance(tx_date, str):
                tx_date = datetime.fromisoformat(tx_date.replace("Z", "+00:00"))
            hour = tx_date.hour if hasattr(tx_date, "hour") else 0
            amount = Decimal(str(tx.get("amount", 0)))
            if tx.get("type") == "expense" and amount > 500 and (hour >= 23 or hour <= 5):
                alerts.append({
                    "type": "late_night_large",
                    "transaction_id": tx.get("id"),
                    "amount": float(amount),
                    "message": f"检测到深夜大额消费 ¥{amount}，请确认是否为本人操作。",
                })
        return alerts

    def _detect_category_spike(self, transactions: List[Dict[str, Any]]) -> List[dict]:
        """检测单日同类消费超均值 3 倍"""
        from collections import defaultdict
        category_daily: Dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
        for tx in transactions:
            if tx.get("type") == "expense":
                cat = tx.get("category_name") or tx.get("category_id") or "未知"
                category_daily[str(cat)] += Decimal(str(tx.get("amount", 0)))

        if not category_daily:
            return []

        avg = sum(category_daily.values(), Decimal("0")) / len(category_daily)
        alerts = []
        for cat, total in category_daily.items():
            if avg > 0 and total > avg * 3:
                alerts.append({
                    "type": "category_spike",
                    "category": cat,
                    "amount": float(total),
                    "message": f"「{cat}」今日支出 ¥{total}，超过近期均值 3 倍，请关注。",
                })
        return alerts
