"""月度报告生成异步任务"""

from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from celery import shared_task
from celery.utils.log import get_task_logger

from infrastructure.db import async_session_master
from models.user import User
from models.transaction import Transaction
from models.monthly_report import MonthlyReport

logger = get_task_logger(__name__)


def _next_month(year_month: str) -> str:
    """计算下个月的第一天字符串，用于范围查询"""
    y, m = int(year_month[:4]), int(year_month[5:7])
    if m == 12:
        return f"{y + 1}-01-01"
    return f"{y}-{m + 1:02d}-01"


async def _generate_report_for_user(session: AsyncSession, user_id: int, year_month: str):
    income_result = await session.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.user_id == user_id,
            Transaction.type == "income",
            Transaction.is_deleted == False,
            Transaction.transaction_date >= f"{year_month}-01",
            Transaction.transaction_date < _next_month(year_month),
        )
    )
    total_income = income_result.scalar() or 0

    expense_result = await session.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.is_deleted == False,
            Transaction.transaction_date >= f"{year_month}-01",
            Transaction.transaction_date < _next_month(year_month),
        )
    )
    total_expense = expense_result.scalar() or 0

    existing = await session.execute(
        select(MonthlyReport).where(
            MonthlyReport.user_id == user_id,
            MonthlyReport.year_month == year_month,
        )
    )
    report = existing.scalar_one_or_none()

    if report:
        report.total_income = total_income
        report.total_expense = total_expense
        report.balance = total_income - total_expense
        session.add(report)
    else:
        report = MonthlyReport(
            user_id=user_id,
            year_month=year_month,
            total_income=total_income,
            total_expense=total_expense,
            balance=total_income - total_expense,
        )
        session.add(report)

    await session.commit()
    logger.info(f"Generated report for user {user_id}, month {year_month}")


@shared_task(name="tasks.report_tasks.generate_monthly_report_for_all_users")
def generate_monthly_report_for_all_users():
    import asyncio

    async def _run():
        year_month = datetime.utcnow().strftime("%Y-%m")
        async with async_session_master() as session:
            result = await session.execute(
                select(User.id).where(User.is_deleted == False)
            )
            user_ids = [row[0] for row in result.all()]

            for uid in user_ids:
                try:
                    await _generate_report_for_user(session, uid, year_month)
                except Exception as e:
                    logger.error(f"Failed to generate report for user {uid}: {e}")

        return f"Reports generated for {datetime.utcnow().isoformat()}"

    asyncio.run(_run())


@shared_task(name="tasks.report_tasks.generate_monthly_report")
def generate_monthly_report(user_id: int, year_month: str = None):
    import asyncio

    async def _run():
        ym = year_month or datetime.utcnow().strftime("%Y-%m")
        async with async_session_master() as session:
            await _generate_report_for_user(session, user_id, ym)

        return f"Report generated for user {user_id}"

    asyncio.run(_run())
