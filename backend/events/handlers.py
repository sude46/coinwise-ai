"""事件处理器（触发 Celery 任务）"""

import json
import logging
from events.event_bus import event_bus
from tasks.budget_tasks import check_budget_alert
from tasks.agent_tasks import run_agent_task
from tasks.transaction_tasks import sync_transaction_to_es
from infrastructure.factory import get_celery

logger = logging.getLogger(__name__)


def _get_celery_app():
    return get_celery()


@event_bus.subscribe("transaction.created")
async def on_transaction_created(event):
    """交易创建后：同步ES、检查预算、触发智能分类、存钱计划对账、审计日志"""
    user_id = event.get("user_id")
    category_id = event.get("category_id")
    tx_id = event.get("tx_id")
    goal_id = event.get("goal_id")

    celery_app = _get_celery_app()

    # 0. 同步到 Elasticsearch（异步）
    if tx_id:
        try:
            sync_transaction_to_es.delay(tx_id)
        except Exception as e:
            logger.error(f"Failed to trigger ES sync: {e}")

    # 1. 检查预算（异步）
    if category_id:
        try:
            check_budget_alert.delay(user_id=user_id, category_id=category_id)
        except Exception as e:
            logger.error(f"Failed to trigger budget check: {e}")

    # 2. 如果分类为空，触发智能分类 Agent
    if category_id is None:
        try:
            run_agent_task.delay("classify", event)
        except Exception as e:
            logger.error(f"Failed to trigger classify agent: {e}")

    # 3. 存钱计划对账（异步，最终一致）
    if goal_id:
        try:
            celery_app.send_task("tasks.reconciliation_tasks.reconcile_goal_amount", args=[goal_id])
        except Exception as e:
            logger.error(f"Failed to trigger reconciliation: {e}")

    # 4. 审计日志（异步）
    try:
        celery_app.send_task("tasks.audit_tasks.write_audit_log", kwargs={
            "user_id": user_id,
            "action": "CREATE",
            "resource": "transaction",
            "resource_id": tx_id,
            "detail": json.dumps({"amount": event.get("amount"), "type": event.get("type")}, ensure_ascii=False),
        })
    except Exception as e:
        logger.error(f"Failed to trigger audit log: {e}")


@event_bus.subscribe("transaction.updated")
async def on_transaction_updated(event):
    """交易更新后：同步ES、重新检查预算、对账、审计日志"""
    user_id = event.get("user_id")
    category_id = event.get("category_id")
    tx_id = event.get("tx_id")
    goal_id = event.get("goal_id")

    celery_app = _get_celery_app()

    if tx_id:
        try:
            sync_transaction_to_es.delay(tx_id)
        except Exception as e:
            logger.error(f"Failed to trigger ES sync on update: {e}")

    if category_id:
        try:
            check_budget_alert.delay(user_id=user_id, category_id=category_id)
        except Exception as e:
            logger.error(f"Failed to trigger budget check on update: {e}")

    if goal_id:
        try:
            celery_app.send_task("tasks.reconciliation_tasks.reconcile_goal_amount", args=[goal_id])
        except Exception as e:
            logger.error(f"Failed to trigger reconciliation on update: {e}")

    try:
        celery_app.send_task("tasks.audit_tasks.write_audit_log", kwargs={
            "user_id": user_id,
            "action": "UPDATE",
            "resource": "transaction",
            "resource_id": tx_id,
            "detail": json.dumps({"amount": event.get("amount"), "type": event.get("type")}, ensure_ascii=False),
        })
    except Exception as e:
        logger.error(f"Failed to trigger audit log on update: {e}")


@event_bus.subscribe("transaction.deleted")
async def on_transaction_deleted(event):
    """交易删除后：同步ES（删除文档）、对账、审计日志"""
    tx_id = event.get("tx_id")
    user_id = event.get("user_id")
    goal_id = event.get("goal_id")

    celery_app = _get_celery_app()

    if tx_id:
        try:
            sync_transaction_to_es.delay(tx_id)
        except Exception as e:
            logger.error(f"Failed to trigger ES sync on delete: {e}")

    if goal_id:
        try:
            celery_app.send_task("tasks.reconciliation_tasks.reconcile_goal_amount", args=[goal_id])
        except Exception as e:
            logger.error(f"Failed to trigger reconciliation on delete: {e}")

    try:
        celery_app.send_task("tasks.audit_tasks.write_audit_log", kwargs={
            "user_id": user_id,
            "action": "DELETE",
            "resource": "transaction",
            "resource_id": tx_id,
            "detail": json.dumps({"year_month": event.get("year_month")}, ensure_ascii=False),
        })
    except Exception as e:
        logger.error(f"Failed to trigger audit log on delete: {e}")


@event_bus.subscribe("savings_goal.created")
async def on_savings_goal_created(event: dict):
    """储蓄目标创建后触发 Celery 对账任务"""
    from tasks.savings_goal_tasks import reconcile_savings_goal
    reconcile_savings_goal.delay(event["user_id"], event["goal_id"])


@event_bus.subscribe("savings_goal.progress_updated")
async def on_savings_goal_progress_updated(event: dict):
    """进度更新后同步到 ES"""
    from tasks.savings_goal_tasks import sync_savings_goal_to_es
    sync_savings_goal_to_es.delay(event["goal_id"])
