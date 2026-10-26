"""预算检查异步任务"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from celery import shared_task
from celery.utils.log import get_task_logger

from core.config import settings
from infrastructure.db import master_engine, async_session_master
from models.user import User
from models.budget import Budget
from models.transaction import Transaction

logger = get_task_logger(__name__)


async def _check_user_budgets(session: AsyncSession, user_id: int, year_month: str):
    budgets_result = await session.execute(
        select(Budget).where(
            Budget.user_id == user_id,
            Budget.year_month == year_month,
            Budget.is_deleted == False,
        )
    )
    budgets = budgets_result.scalars().all()

    alerts = []
    for budget in budgets:
        expense_result = await session.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                Transaction.user_id == user_id,
                Transaction.category_id == budget.category_id,
                Transaction.type == "expense",
                Transaction.is_deleted == False,
                Transaction.transaction_date >= f"{year_month}-01",
                Transaction.transaction_date < _next_month(year_month),
            )
        )
        total_spent = expense_result.scalar() or Decimal("0")

        if total_spent >= budget.limit_amount:
            alerts.append({
                "user_id": user_id,
                "budget_id": budget.id,
                "category_id": budget.category_id,
                "limit_amount": float(budget.limit_amount),
                "total_spent": float(total_spent),
                "percentage": float(total_spent / budget.limit_amount * 100) if budget.limit_amount > 0 else 0,
            })

    if alerts:
        logger.warning(f"Budget alerts for user {user_id}: {len(alerts)} budgets exceeded")

    return alerts


def _next_month(year_month: str) -> str:
    """计算下个月的第一天字符串，用于范围查询"""
    y, m = int(year_month[:4]), int(year_month[5:7])
    if m == 12:
        return f"{y + 1}-01-01"
    return f"{y}-{m + 1:02d}-01"


@shared_task(name="tasks.budget_tasks.check_budget_alerts_for_all_users")
def check_budget_alerts_for_all_users():
    import asyncio

    async def _run():
        year_month = datetime.utcnow().strftime("%Y-%m")
        async with async_session_master() as session:
            result = await session.execute(
                select(User.id).where(User.is_deleted == False)
            )
            user_ids = [row[0] for row in result.all()]

            all_alerts = []
            for uid in user_ids:
                try:
                    alerts = await _check_user_budgets(session, uid, year_month)
                    all_alerts.extend(alerts)
                except Exception as e:
                    logger.error(f"Failed to check budget for user {uid}: {e}")
            await session.commit()

        return all_alerts

    return asyncio.run(_run()) or []


@shared_task(name="tasks.budget_tasks.check_budget_alert")
def check_budget_alert(user_id: int, category_id: int):
    import asyncio

    async def _run():
        year_month = datetime.utcnow().strftime("%Y-%m")
        async with async_session_master() as session:
            budget_result = await session.execute(
                select(Budget).where(
                    Budget.user_id == user_id,
                    Budget.category_id == category_id,
                    Budget.year_month == year_month,
                    Budget.is_deleted == False,
                )
            )
            budget = budget_result.scalar_one_or_none()

            if not budget:
                return None

            expense_result = await session.execute(
                select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                    Transaction.user_id == user_id,
                    Transaction.category_id == category_id,
                    Transaction.type == "expense",
                    Transaction.is_deleted == False,
                    Transaction.transaction_date >= f"{year_month}-01",
                    Transaction.transaction_date < _next_month(year_month),
                )
            )
            total_spent = expense_result.scalar() or Decimal("0")

            exceeded = total_spent >= budget.limit_amount

            await session.commit()
            return {
                "user_id": user_id,
                "category_id": category_id,
                "limit": float(budget.limit_amount),
                "spent": float(total_spent),
                "exceeded": exceeded,
            }

    return asyncio.run(_run())
