from .base import BaseAgent
from .alert_agent import BudgetAlertAgent
from .classify_agent import SmartCategoryAgent as ClassifyAgent
from .report_agent import MonthlyReportAgent as ReportAgent
from .nl_transaction import NLTransactionAgent
from .finance_strategy import FinanceStrategyAgent
from .anomaly import AnomalyAgent

AGENT_REGISTRY = {
    "alert": BudgetAlertAgent,
    "classify": ClassifyAgent,
    "report": ReportAgent,
    "nl_transaction": NLTransactionAgent,
    "finance_strategy": FinanceStrategyAgent,
    "anomaly": AnomalyAgent,
}
