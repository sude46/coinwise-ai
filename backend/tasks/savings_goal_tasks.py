import logging
from tasks.celery_app import celery_app
from core.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(name="savings_goal.reconcile")
def reconcile_savings_goal(user_id: int, goal_id: int):
    """异步对账：委托给新的 reconciliation_tasks（基于 savings_records）"""
    from tasks.reconciliation_tasks import reconcile_goal_amount
    reconcile_goal_amount.delay(goal_id)


@celery_app.task(name="savings_goal.sync_es")
def sync_savings_goal_to_es(goal_id: int):
    """将储蓄目标同步到 Elasticsearch（ES 默认关闭时跳过）"""
    if not getattr(settings, "ES_ENABLED", False):
        logger.debug("ES is disabled, skipping savings goal sync")
        return
    # 保留接口，实际同步逻辑待 ES 启用时实现
    logger.info(f"Savings goal {goal_id} ES sync skipped (ES disabled)")
