"""UnitOfWork：跨多个 Repository 的统一事务管理"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.factory import get_db_session
from repositories.user import UserRepository
from repositories.transaction import TransactionRepository
from repositories.category import CategoryRepository
from repositories.budget import BudgetRepository
from repositories.monthly_report import MonthlyReportRepository
from repositories.account import AccountRepository
from repositories.audit_log import AuditLogRepository
from repositories.savings_goal import SavingsGoalRepository
from repositories.savings_record import SavingsRecordRepository


class UnitOfWork:
    """
    工作单元模式
    用法：
        async with UnitOfWork(for_write=True) as uow:
            uow.transaction_repo.create(...)
            uow.budget_repo.update(...)
            # 退出时自动 commit，异常时自动 rollback
    """

    def __init__(self, for_write: bool = False):
        self.for_write = for_write
        self.session: Optional[AsyncSession] = None

    async def __aenter__(self):
        self._cm = get_db_session(for_write=self.for_write)
        self.session = await self._cm.__aenter__()

        # 初始化所有 Repository
        self.user_repo = UserRepository(self.session)
        self.transaction_repo = TransactionRepository(self.session)
        self.category_repo = CategoryRepository(self.session)
        self.budget_repo = BudgetRepository(self.session)
        self.report_repo = MonthlyReportRepository(self.session)
        self.account_repo = AccountRepository(self.session)
        self.audit_log_repo = AuditLogRepository(self.session)
        self.savings_goal_repo = SavingsGoalRepository(self.session)
        self.savings_record_repo = SavingsRecordRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self._cm.__aexit__(exc_type, exc_val, exc_tb)
