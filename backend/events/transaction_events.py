import logging
from sqlalchemy.ext.asyncio import AsyncSession
from services.report import ReportService
from services.budget import BudgetService
from models.transaction import Transaction
from tasks.budget_tasks import check_budget_alert

logger = logging.getLogger(__name__)


async def _refresh_report(session: AsyncSession, user_id: int, year_month: str):
    """刷新用户月报"""
    try:
        report_service = ReportService(session)
        await report_service.get_or_generate_report(user_id, year_month)
        logger.info(f"Report refreshed for user {user_id}, month {year_month}")
    except Exception as e:
        logger.error(f"Failed to refresh report for user {user_id}, month {year_month}: {e}")


async def _trigger_budget_check(user_id: int, category_id: int):
    """异步触发预算检查"""
    try:
        check_budget_alert.delay(user_id=user_id, category_id=category_id)
        logger.info(f"Budget check triggered for user {user_id}, category {category_id}")
    except Exception as e:
        logger.error(f"Failed to trigger budget check: {e}")


async def on_transaction_created(session: AsyncSession, transaction: Transaction):
    """
    交易创建后的事件处理：
    1. 刷新对应月份的月报
    2. 如果是支出，检查对应分类预算是否超支
    """
    year_month = transaction.transaction_date.strftime("%Y-%m")
    await _refresh_report(session, transaction.user_id, year_month)

    if transaction.type == "expense" and transaction.category_id:
        await _trigger_budget_check(transaction.user_id, transaction.category_id)


async def on_transaction_updated(session: AsyncSession, transaction: Transaction):
    """
    交易更新后的事件处理：
    1. 刷新对应月份的月报
    2. 如果是支出，检查对应分类预算
    """
    year_month = transaction.transaction_date.strftime("%Y-%m")
    await _refresh_report(session, transaction.user_id, year_month)

    if transaction.type == "expense" and transaction.category_id:
        await _trigger_budget_check(transaction.user_id, transaction.category_id)


async def on_transaction_deleted(session: AsyncSession, user_id: int, year_month: str, category_id: int = None, transaction_type: str = None):
    """
    交易删除后的事件处理：
    1. 刷新月报（支出减少，预算可能回到正常）
    2. 重新检查预算
    """
    await _refresh_report(session, user_id, year_month)

    if transaction_type == "expense" and category_id:
        await _trigger_budget_check(user_id, category_id)