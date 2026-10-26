from typing import List
from decimal import Decimal
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from repositories.monthly_report import MonthlyReportRepository
from repositories.transaction import TransactionRepository
from models.monthly_report import MonthlyReport
from models.transaction import Transaction


class ReportService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.report_repo = MonthlyReportRepository(session)
        self.transaction_repo = TransactionRepository(session)

    async def get_or_generate_report(self, user_id: int, year_month: str) -> MonthlyReport:
        existing = await self.report_repo.get_by_user_month(user_id, year_month)
        if existing:
            return existing

        start_date = datetime.strptime(f"{year_month}-01", "%Y-%m-%d")
        if start_date.month == 12:
            end_date = start_date.replace(year=start_date.year + 1, month=1)
        else:
            end_date = start_date.replace(month=start_date.month + 1)

        date_filter = and_(
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date < end_date,
        )

        income_result = await self.session.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                Transaction.user_id == user_id,
                Transaction.type == "income",
                Transaction.is_deleted == False,
                date_filter,
            )
        )
        total_income = income_result.scalar() or Decimal("0")

        expense_result = await self.session.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                Transaction.user_id == user_id,
                Transaction.type == "expense",
                Transaction.is_deleted == False,
                date_filter,
            )
        )
        total_expense = expense_result.scalar() or Decimal("0")

        report = MonthlyReport(
            user_id=user_id,
            year_month=year_month,
            total_income=total_income,
            total_expense=total_expense,
            balance=total_income - total_expense,
        )
        return await self.report_repo.get_or_create(report)

    async def list_reports(self, user_id: int) -> List[MonthlyReport]:
        return await self.report_repo.list_by_user(user_id)
