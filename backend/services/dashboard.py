from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, cast, Date
from dateutil.relativedelta import relativedelta

from models.transaction import Transaction
from models.budget import Budget
from models.category import Category
from services.account import AccountService
from infrastructure.crypto import crypto


class DashboardService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_dashboard(self, user_id: int, year_month: str) -> Dict[str, Any]:
        month_income = await self._get_monthly_income(user_id, year_month)
        month_expense = await self._get_monthly_expense(user_id, year_month)
        balance = month_income - month_expense

        budget_breakdown = await self._get_budget_breakdown(user_id, year_month)
        total_budget = sum(b["limit_amount"] for b in budget_breakdown)
        matched_expense = sum(b["spent"] for b in budget_breakdown)
        budget_remaining = total_budget - matched_expense

        account_service = AccountService(self.session)
        wallet_balance = await account_service.get_total_balance(user_id)

        recent_transactions = await self._get_recent_transactions(user_id)
        category_pie = await self._get_category_pie(user_id, year_month)
        trend = await self._get_trend(user_id)
        daily_trend = await self._get_daily_trend(user_id, days=7)

        return {
            "month_income": float(month_income),
            "month_expense": float(month_expense),
            "balance": float(balance),
            "budget_remaining": float(budget_remaining),
            "total_budget": float(total_budget),
            "budget_breakdown": budget_breakdown,
            "wallet_balance": float(wallet_balance),
            "recent_transactions": recent_transactions,
            "category_pie": category_pie,
            "trend": trend,
            "daily_trend": daily_trend,
        }

    async def _get_budget_breakdown(self, user_id: int, year_month: str) -> List[Dict[str, Any]]:
        budget_rows = await self.session.execute(
            select(
                Budget.id,
                Budget.limit_amount,
                Budget.category_id,
                Category.name,
                Category.icon,
            )
            .outerjoin(Category, Budget.category_id == Category.id)
            .where(
                Budget.user_id == user_id,
                Budget.year_month == year_month,
                Budget.is_deleted == False,
            )
        )
        breakdown = []
        for row in budget_rows.all():
            spent = Decimal("0")
            if row.category_id:
                spent = await self._get_category_expense(user_id, row.category_id, year_month)
            breakdown.append({
                "budget_id": row.id,
                "category_id": row.category_id,
                "category_name": row.name or "未分类",
                "icon": row.icon or "📦",
                "limit_amount": float(row.limit_amount),
                "spent": float(spent),
                "remaining": float(row.limit_amount - spent),
            })
        return breakdown

    async def _get_category_expense(self, user_id: int, category_id: int, year_month: str) -> Decimal:
        result = await self.session.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                Transaction.user_id == user_id,
                Transaction.category_id == category_id,
                Transaction.type == "expense",
                Transaction.is_deleted == False,
                self._year_month_filter(Transaction.transaction_date, year_month),
            )
        )
        return result.scalar() or Decimal("0")

    async def _get_monthly_income(self, user_id: int, year_month: str) -> Decimal:
        result = await self.session.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                Transaction.user_id == user_id,
                Transaction.type == "income",
                Transaction.is_deleted == False,
                self._year_month_filter(Transaction.transaction_date, year_month),
            )
        )
        return result.scalar() or Decimal("0")

    async def _get_monthly_expense(self, user_id: int, year_month: str) -> Decimal:
        result = await self.session.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                Transaction.user_id == user_id,
                Transaction.type == "expense",
                Transaction.is_deleted == False,
                self._year_month_filter(Transaction.transaction_date, year_month),
            )
        )
        return result.scalar() or Decimal("0")

    async def _get_total_budget(self, user_id: int, year_month: str) -> Decimal:
        result = await self.session.execute(
            select(func.coalesce(func.sum(Budget.limit_amount), 0)).where(
                Budget.user_id == user_id,
                Budget.year_month == year_month,
                Budget.is_deleted == False,
            )
        )
        return result.scalar() or Decimal("0")

    async def _get_recent_transactions(self, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        result = await self.session.execute(
            select(
                Transaction.id,
                Transaction.user_id,
                Transaction.category_id,
                Transaction.account_id,
                Transaction.goal_id,
                Transaction.type,
                Transaction.amount,
                Transaction.remark,
                Transaction.source,
                Transaction.transaction_date,
                Transaction.created_at,
                Category.name.label("category_name"),
                Category.icon.label("category_icon"),
            )
            .outerjoin(Category, Transaction.category_id == Category.id)
            .where(
                Transaction.user_id == user_id,
                Transaction.is_deleted == False,
            )
            .order_by(Transaction.transaction_date.desc())
            .limit(limit)
        )
        rows = []
        for row in result.all():
            rows.append({
                "id": row.id,
                "user_id": row.user_id,
                "category_id": row.category_id,
                "account_id": row.account_id,
                "goal_id": row.goal_id,
                "type": row.type,
                "amount": float(row.amount),
                "remark": crypto.decrypt(row.remark) if row.remark else None,
                "source": row.source,
                "transaction_date": row.transaction_date,
                "created_at": row.created_at,
                "category": {
                    "id": row.category_id,
                    "name": row.category_name,
                    "icon": row.category_icon,
                } if row.category_id else None,
            })
        return rows

    async def _get_category_pie(self, user_id: int, year_month: str) -> List[Dict[str, Any]]:
        result = await self.session.execute(
            select(
                Category.name.label("name"),
                func.coalesce(func.sum(Transaction.amount), 0).label("value"),
            )
            .join(Category, Transaction.category_id == Category.id)
            .where(
                Transaction.user_id == user_id,
                Transaction.type == "expense",
                Transaction.is_deleted == False,
                self._year_month_filter(Transaction.transaction_date, year_month),
            )
            .group_by(Category.id, Category.name)
        )
        return [{"name": row.name, "value": float(row.value)} for row in result.all()]

    async def _get_daily_trend(self, user_id: int, days: int = 7) -> List[Dict[str, Any]]:
        end = datetime.utcnow().replace(hour=23, minute=59, second=59)
        start = end - timedelta(days=days - 1)
        start = start.replace(hour=0, minute=0, second=0)

        result = await self.session.execute(
            select(
                cast(Transaction.transaction_date, Date).label("date"),
                Transaction.type,
                func.coalesce(func.sum(Transaction.amount), 0).label("total"),
            ).where(
                Transaction.user_id == user_id,
                Transaction.is_deleted == False,
                Transaction.transaction_date >= start,
                Transaction.transaction_date <= end,
            ).group_by(
                cast(Transaction.transaction_date, Date),
                Transaction.type,
            ).order_by(cast(Transaction.transaction_date, Date))
        )

        data_map = {}
        for row in result.all():
            date_str = row.date.isoformat()
            if date_str not in data_map:
                data_map[date_str] = {"income": 0, "expense": 0}
            data_map[date_str][row.type] = float(row.total)

        daily = []
        current = start.date()
        end_date = end.date()
        while current <= end_date:
            date_str = current.isoformat()
            day = data_map.get(date_str, {"income": 0, "expense": 0})
            daily.append({
                "date": date_str,
                "label": current.strftime("%m-%d"),
                "income": day["income"],
                "expense": day["expense"],
            })
            current += timedelta(days=1)
        return daily

    async def _get_trend(self, user_id: int, months: int = 6) -> List[Dict[str, Any]]:
        trend = []
        for i in range(months - 1, -1, -1):
            dt = datetime.utcnow() - relativedelta(months=i)
            ym = dt.strftime("%Y-%m")
            inc = await self.session.execute(
                select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                    Transaction.user_id == user_id,
                    Transaction.type == "income",
                    Transaction.is_deleted == False,
                    self._year_month_filter(Transaction.transaction_date, ym),
                )
            )
            exp = await self.session.execute(
                select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                    Transaction.user_id == user_id,
                    Transaction.type == "expense",
                    Transaction.is_deleted == False,
                    self._year_month_filter(Transaction.transaction_date, ym),
                )
            )
            trend.append({
                "month": ym,
                "income": float(inc.scalar() or 0),
                "expense": float(exp.scalar() or 0),
            })
        return trend

    @staticmethod
    def _year_month_filter(date_column, year_month: str):
        start = datetime.strptime(f"{year_month}-01", "%Y-%m-%d")
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1)
        else:
            end = start.replace(month=start.month + 1)
        return and_(date_column >= start, date_column < end)
