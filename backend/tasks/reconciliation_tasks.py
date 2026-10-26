"""存钱计划金额对账任务 — 最终一致性

根据 savings_records 汇总更新 savings_goals.current_amount，
允许短暂不一致，失败时 Celery 重试 3 次。
"""

from celery import shared_task
from celery.utils.log import get_task_logger
from sqlalchemy import select, update as sa_update
from decimal import Decimal

from infrastructure.db import async_session_master
from models.savings_goal import SavingsGoal
from models.savings_record import SavingsRecord

logger = get_task_logger(__name__)


@shared_task(name="tasks.reconciliation_tasks.reconcile_goal_amount", bind=True, max_retries=3)
def reconcile_goal_amount(self, goal_id: int):
    """定时对账：根据 savings_records 汇总更新 current_amount"""
    import asyncio

    async def _run():
        async with async_session_master() as session:
            # 1. 计算该 goal 下所有关联记录的 amount 总和
            result = await session.execute(
                select(SavingsGoal).where(SavingsGoal.id == goal_id)
            )
            goal = result.scalar_one_or_none()
            if not goal:
                logger.warning(f"Goal {goal_id} not found, skipping reconciliation")
                return

            sum_result = await session.execute(
                select(SavingsRecord.amount).where(SavingsRecord.goal_id == goal_id)
            )
            amounts = sum_result.scalars().all()
            total = sum(amounts, Decimal("0"))

            # 2. 更新 goals 表（允许短暂不一致，最终一致）
            await session.execute(
                sa_update(SavingsGoal)
                .where(SavingsGoal.id == goal_id)
                .values(current_amount=total)
            )
            await session.commit()
            logger.info(f"Reconciled goal {goal_id}: current_amount = {total}")

            # 3. 检查是否已达成目标
            if total >= goal.target_amount and goal.status == "active":
                await session.execute(
                    sa_update(SavingsGoal)
                    .where(SavingsGoal.id == goal_id)
                    .values(status="completed")
                )
                await session.commit()
                logger.info(f"Goal {goal_id} marked as completed")

    try:
        asyncio.run(_run())
    except Exception as exc:
        logger.error(f"Reconciliation failed for goal {goal_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(name="tasks.reconciliation_tasks.reconcile_all_active_goals")
def reconcile_all_active_goals():
    """定时任务：对所有活跃存钱计划执行对账"""
    import asyncio

    async def _run():
        async with async_session_master() as session:
            result = await session.execute(
                select(SavingsGoal.id).where(
                    SavingsGoal.status == "active",
                    SavingsGoal.is_deleted == False,
                )
            )
            goal_ids = [row[0] for row in result.all()]
            for gid in goal_ids:
                try:
                    reconcile_goal_amount.delay(gid)
                except Exception as exc:
                    logger.error(f"Failed to enqueue reconciliation for goal {gid}: {exc}")

    asyncio.run(_run())
