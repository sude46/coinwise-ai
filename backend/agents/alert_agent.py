"""预算超支预警 Agent + 多渠道通知投递"""
from decimal import Decimal
from agents.base import BaseAgent


class BudgetAlertAgent(BaseAgent):
    name = "alert"

    async def execute(self, payload: dict) -> dict:
        limit_amount = Decimal(str(payload.get("limit_amount", 0)))
        total_spent = Decimal(str(payload.get("total_spent", 0)))
        category_name = payload.get("category_name", "未知分类")
        percentage = float(total_spent / limit_amount * 100) if limit_amount > 0 else 0

        exceeded = total_spent >= limit_amount
        warning_level = "normal"
        if exceeded:
            warning_level = "danger"
        elif percentage >= 80:
            warning_level = "warning"

        result = {
            "user_id": payload.get("user_id"),
            "category_name": category_name,
            "limit_amount": float(limit_amount),
            "total_spent": float(total_spent),
            "percentage": round(percentage, 2),
            "exceeded": exceeded,
            "warning_level": warning_level,
            "message": (
                f"【超支预警】{category_name} 本月预算 {limit_amount} 元，"
                f"已支出 {total_spent} 元（{percentage:.1f}%）"
                if exceeded
                else f"{category_name} 支出进度 {percentage:.1f}%"
            ),
        }

        if exceeded or warning_level == "warning":
            await self._send_notifications(result)

        return result

    async def _send_notifications(self, alert: dict):
        from services.notification import notification_service
        user_id = alert.get("user_id")
        category_name = alert.get("category_name", "未知分类")
        limit_amount = alert.get("limit_amount", 0)
        total_spent = alert.get("total_spent", 0)

        from infrastructure.db import async_session_master
        from models.user import User
        from sqlalchemy import select

        async with async_session_master() as session:
            user_result = await session.execute(
                select(User).where(User.id == user_id, User.is_deleted == False)
            )
            user = user_result.scalar_one_or_none()
            if user and user.email:
                await notification_service.send_budget_alert(
                    to=user.email,
                    user_id=user_id,
                    category_name=category_name,
                    limit_amount=limit_amount,
                    total_spent=total_spent,
                )
