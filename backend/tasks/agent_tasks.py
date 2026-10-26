"""Agent 执行器"""

import asyncio
import hashlib
import json
from celery import shared_task
from celery.utils.log import get_task_logger

from agents import AGENT_REGISTRY

logger = get_task_logger(__name__)


@shared_task(name="tasks.agent_tasks.run_agent_task", max_retries=3)
def run_agent_task(task_type: str, payload: dict):
    """执行 Agent 任务，支持幂等"""
    agent_class = AGENT_REGISTRY.get(task_type)
    if not agent_class:
        logger.error(f"Unknown agent type: {task_type}")
        raise ValueError(f"Unknown agent: {task_type}")

    # 幂等键
    user_id = payload.get("user_id", "unknown")
    payload_hash = hashlib.md5(
        json.dumps(payload, sort_keys=True, default=str).encode()
    ).hexdigest()
    pending_id = hashlib.md5(
        f"{user_id}:{task_type}:{payload_hash}".encode()
    ).hexdigest()

    logger.info(f"Running agent {task_type}, pending_id={pending_id}")

    async def _execute():
        agent = agent_class()
        return await agent.execute(payload)

    try:
        result = asyncio.run(_execute())
        logger.info(f"Agent {task_type} completed: {result}")
        return result
    except Exception as exc:
        logger.error(f"Agent {task_type} failed: {exc}")
        raise run_agent_task.retry(exc=exc, countdown=60)
