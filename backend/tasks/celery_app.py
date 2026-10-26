from celery import Celery
from core.config import settings

celery_app = Celery(
    "coinwise",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "tasks.report_tasks",
        "tasks.budget_tasks",
        "tasks.transaction_tasks",
        "tasks.agent_tasks",
        "tasks.reconciliation_tasks",
        "tasks.audit_tasks",
        "tasks.savings_goal_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    beat_schedule={
        "generate-monthly-reports": {
            "task": "tasks.report_tasks.generate_monthly_report_for_all_users",
            "schedule": 3600.0,  # 每小时执行一次
        },
        "check-budget-alerts": {
            "task": "tasks.budget_tasks.check_budget_alerts_for_all_users",
            "schedule": 600.0,  # 每10分钟执行一次
        },
        "reconcile-all-active-goals": {
            "task": "tasks.reconciliation_tasks.reconcile_all_active_goals",
            "schedule": 3600.0,  # 每小时对账一次
        },
    },
)
