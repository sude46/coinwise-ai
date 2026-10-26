"""月度分析 Agent"""

from decimal import Decimal
from agents.base import BaseAgent


class MonthlyReportAgent(BaseAgent):
    name = "report"

    async def execute(self, payload: dict) -> dict:
        """
        根据月度收支数据生成分析报告。
        payload 包含 total_income, total_expense, balance, category_breakdown 等。
        """
        total_income = Decimal(str(payload.get("total_income", 0)))
        total_expense = Decimal(str(payload.get("total_expense", 0)))
        balance = Decimal(str(payload.get("balance", 0)))
        category_breakdown = payload.get("category_breakdown", [])
        year_month = payload.get("year_month", "")

        # 找出最大支出分类
        top_expense_category = None
        if category_breakdown:
            sorted_categories = sorted(
                category_breakdown,
                key=lambda x: Decimal(str(x.get("amount", 0))),
                reverse=True,
            )
            top_expense_category = sorted_categories[0]

        # 生成简单分析文本
        analysis = f"## {year_month} 月度财务分析报告\n\n"
        analysis += f"- **总收入**: {total_income} 元\n"
        analysis += f"- **总支出**: {total_expense} 元\n"
        analysis += f"- **结余**: {balance} 元\n\n"

        if total_income > 0:
            savings_rate = float(balance / total_income * 100)
            analysis += f"- **储蓄率**: {savings_rate:.1f}%\n\n"

        if top_expense_category:
            analysis += f"### 最大支出项\n"
            analysis += f"- **{top_expense_category['name']}**: {top_expense_category['amount']} 元\n\n"

        if balance < 0:
            analysis += "⚠️ **警告**: 本月支出超过收入，建议审视非必要开支。\n"
        elif savings_rate < 20:
            analysis += "💡 **建议**: 储蓄率偏低，可以尝试制定更严格的预算计划。\n"
        else:
            analysis += "✅ **评价**: 财务状况良好，继续保持！\n"

        return {
            "user_id": payload.get("user_id"),
            "year_month": year_month,
            "total_income": float(total_income),
            "total_expense": float(total_expense),
            "balance": float(balance),
            "analysis": analysis,
            "top_expense_category": top_expense_category,
        }
