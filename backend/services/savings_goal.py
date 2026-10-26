from typing import Optional
from datetime import datetime, timedelta
from decimal import Decimal

from models.savings_goal import SavingsGoal
from models.savings_record import SavingsRecord
from repositories.savings_goal import SavingsGoalRepository
from repositories.savings_record import SavingsRecordRepository
from schemas.savings_goal import SavingsGoalCreate, SavingsGoalUpdate, SavingsGoalOut, SavingsGoalPredictOut
from core.exceptions import NotFoundException


class SavingsGoalService:
    def __init__(self, repo: SavingsGoalRepository, record_repo: Optional[SavingsRecordRepository] = None):
        self._repo = repo
        self._record_repo = record_repo

    async def create(self, user_id: int, data: SavingsGoalCreate) -> SavingsGoalOut:
        goal = SavingsGoal(
            tenant_id=0,
            user_id=user_id,
            category_id=data.category_id,
            name=data.name,
            target_amount=data.target_amount,
            start_date=data.start_date,
            end_date=data.end_date,
            note=data.note,
            created_by=user_id,
        )
        saved = await self._repo.create(goal)
        return SavingsGoalOut.model_validate(saved)

    async def get(self, goal_id: int, user_id: int) -> SavingsGoalOut:
        goal = await self._repo.get_by_id(goal_id, user_id)
        if not goal:
            raise NotFoundException("储蓄目标不存在")
        return SavingsGoalOut.model_validate(goal)

    async def list_for_user(
        self, user_id: int, status: Optional[str] = None, offset: int = 0, limit: int = 20
    ) -> tuple[list[SavingsGoalOut], int]:
        rows, total = await self._repo.list_by_user(user_id, status, offset, limit)
        return [SavingsGoalOut.model_validate(r) for r in rows], total

    async def update(self, goal_id: int, user_id: int, data: SavingsGoalUpdate) -> SavingsGoalOut:
        goal = await self._repo.get_by_id(goal_id, user_id)
        if not goal:
            raise NotFoundException("储蓄目标不存在")
        update_data = data.model_dump(exclude_unset=True)
        update_data["updated_by"] = user_id
        updated = await self._repo.update(goal, **update_data)
        return SavingsGoalOut.model_validate(updated)

    async def delete(self, goal_id: int, user_id: int) -> None:
        goal = await self._repo.get_by_id(goal_id, user_id)
        if not goal:
            raise NotFoundException("储蓄目标不存在")
        await self._repo.soft_delete(goal, deleted_by=user_id)

    async def predict_achievement(self, goal_id: int, user_id: int) -> SavingsGoalPredictOut:
        """基于 EMA（指数移动平均）预测存钱计划达成情况"""
        goal = await self._repo.get_by_id(goal_id, user_id)
        if not goal:
            raise NotFoundException("储蓄目标不存在")

        today = datetime.now().date()
        target_date = goal.end_date.date() if hasattr(goal.end_date, "date") else goal.end_date

        remaining = float(goal.target_amount - goal.current_amount)
        days_left = (target_date - today).days

        if days_left <= 0:
            return SavingsGoalPredictOut(
                goal_id=goal_id,
                daily_required=0.0,
                predicted_date=None,
                risk="expired",
                message="计划已过期",
                ema_daily_avg=0.0,
            )

        daily_required = remaining / max(days_left, 1)

        # 获取近期存钱记录（用于 EMA）
        recent_amounts = []
        if self._record_repo:
            records = await self._record_repo.list_by_goal(goal_id, limit=30)
            recent_amounts = [float(r.amount) for r in records]

        if not recent_amounts or len(recent_amounts) < 3:
            return SavingsGoalPredictOut(
                goal_id=goal_id,
                daily_required=round(daily_required, 2),
                predicted_date=None,
                risk="unknown",
                message="存入记录不足，无法预测",
                ema_daily_avg=0.0,
            )

        # 指数移动平均（EMA），最近权重更高
        alpha = 0.3
        ema = recent_amounts[0]
        for record_amount in recent_amounts[1:]:
            ema = alpha * record_amount + (1 - alpha) * ema

        predicted_days = remaining / ema if ema > 0 else float("inf")
        predicted_date = today + timedelta(days=predicted_days)
        delay_days = (predicted_date - target_date).days

        if delay_days > 30:
            risk, message = "critical", f"严重滞后：预计延迟 {delay_days} 天，建议大幅削减非必要开支或增加收入"
        elif delay_days > 14:
            risk, message = "high", f"进度落后：预计延迟 {delay_days} 天，建议调整每日存钱额至 ¥{daily_required:.1f}"
        elif delay_days > 0:
            category_name = "相关"  # 简化，实际可从 category 关联查询
            risk, message = "medium", f"略有滞后：预计延迟 {delay_days} 天，注意控制 {category_name} 分类支出"
        else:
            risk, message = "low", f"进度良好：预计提前 {-delay_days} 天达成"

        return SavingsGoalPredictOut(
            goal_id=goal_id,
            daily_required=round(daily_required, 2),
            predicted_date=predicted_date,
            risk=risk,
            message=message,
            ema_daily_avg=round(ema, 2),
        )
