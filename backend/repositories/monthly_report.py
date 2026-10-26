from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.monthly_report import MonthlyReport


class MonthlyReportRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create(self, report: MonthlyReport) -> MonthlyReport:
        self.session.add(report)
        await self.session.flush()
        return report

    async def get_by_user_month(self, user_id: int, year_month: str) -> Optional[MonthlyReport]:
        result = await self.session.execute(
            select(MonthlyReport).where(
                MonthlyReport.user_id == user_id,
                MonthlyReport.year_month == year_month,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: int) -> List[MonthlyReport]:
        result = await self.session.execute(
            select(MonthlyReport)
            .where(MonthlyReport.user_id == user_id)
            .order_by(MonthlyReport.year_month.desc())
        )
        return list(result.scalars().all())

    async def update(self, report: MonthlyReport, update_data: dict) -> MonthlyReport:
        for key, value in update_data.items():
            if value is not None:
                setattr(report, key, value)
        self.session.add(report)
        return report