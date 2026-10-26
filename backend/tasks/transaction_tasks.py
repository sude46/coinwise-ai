"""记账后异步处理任务"""

from celery import shared_task
from celery.utils.log import get_task_logger
from sqlalchemy import select

from infrastructure.db import async_session_master
from models.transaction import Transaction
from models.category import Category
from core.config import settings

logger = get_task_logger(__name__)


@shared_task(name="tasks.transaction_tasks.sync_to_es")
def sync_transaction_to_es(transaction_id: int):
    """将交易记录同步到 Elasticsearch（ES 默认关闭时跳过）"""
    if not getattr(settings, "ES_ENABLED", False):
        logger.debug("ES is disabled, skipping sync")
        return

    import asyncio
    from infrastructure.factory import get_es

    async def _run():
        async with async_session_master() as session:
            result = await session.execute(
                select(Transaction).where(Transaction.id == transaction_id)
            )
            tx = result.scalar_one_or_none()
            if not tx:
                logger.warning(f"Transaction {transaction_id} not found")
                return

            category_name = ""
            if tx.category_id:
                cat_result = await session.execute(
                    select(Category.name).where(Category.id == tx.category_id)
                )
                category_name = cat_result.scalar() or ""

            es = await get_es()
            doc = {
                "transaction_id": tx.id,
                "user_id": tx.user_id,
                "category_id": tx.category_id,
                "category_name": category_name,
                "type": tx.type,
                "amount": float(tx.amount),
                "remark": tx.remark or "",
                "transaction_date": tx.transaction_date.isoformat() if tx.transaction_date else "",
            }
            await es.index(index="transactions", id=str(tx.id), document=doc)
            logger.info(f"Synced transaction {transaction_id} to ES")

    asyncio.run(_run())
