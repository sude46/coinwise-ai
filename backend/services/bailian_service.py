import json
import logging
import re
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Dict, Any, List
from openai import AsyncOpenAI
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from models.transaction import Transaction
from models.budget import Budget
from models.category import Category

logger = logging.getLogger(__name__)


class BailianService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.BAILIAN_API_KEY,
            base_url=settings.BAILIAN_BASE_URL
        )
        self.model = settings.BAILIAN_MODEL
        self.temperature = settings.BAILIAN_TEMPERATURE
        self.max_tokens = settings.BAILIAN_MAX_TOKENS
        self.top_p = settings.BAILIAN_TOP_P

    async def chat(
        self,
        message: str,
        user_id: int,
        db: AsyncSession,
        conversation_history: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        context = await self._build_user_context(user_id, db)
        system_prompt = self._build_system_prompt(context)

        messages = [{"role": "system", "content": system_prompt}]
        if conversation_history:
            messages.extend(conversation_history[-5:])
        messages.append({"role": "user", "content": message})

        try:
            kwargs = dict(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
            )
            if settings.BAILIAN_ENABLE_SEARCH:
                kwargs["extra_body"] = {"enable_search": True}

            response = await self.client.chat.completions.create(**kwargs)

            ai_reply = response.choices[0].message.content or ""
            action = self._parse_action(ai_reply)
            ai_reply_clean = re.sub(r'\s*\[ACTION:\w+\].*?\[/ACTION\]\s*', '', ai_reply, flags=re.DOTALL).strip()

            return {
                "reply": ai_reply_clean,
                "action": action,
                "model": self.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                },
            }
        except Exception as e:
            logger.exception(f"Bailian API call failed: {e}")
            action = self._fallback_parse(message)
            reply = "好的，我来帮你处理。" if action else f"抱歉，AI 服务暂时不可用。错误: {e}"
            return {
                "reply": reply,
                "action": action,
                "model": self.model,
                "error": str(e),
            }

    async def _build_user_context(self, user_id: int, db: AsyncSession) -> Dict:
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now.replace(day=1, hour=0, minute=0, second=0)

        async def _sum_amount(conditions):
            stmt = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                Transaction.user_id == user_id,
                Transaction.is_deleted == False,
                *conditions,
            )
            result = await db.execute(stmt)
            return float(result.scalar() or 0)

        today_income = await _sum_amount([
            Transaction.type == "income",
            Transaction.transaction_date >= today_start,
        ])
        today_expense = await _sum_amount([
            Transaction.type == "expense",
            Transaction.transaction_date >= today_start,
        ])
        week_income = await _sum_amount([
            Transaction.type == "income",
            Transaction.transaction_date >= week_start,
        ])
        week_expense = await _sum_amount([
            Transaction.type == "expense",
            Transaction.transaction_date >= week_start,
        ])
        month_income = await _sum_amount([
            Transaction.type == "income",
            Transaction.transaction_date >= month_start,
        ])
        month_expense = await _sum_amount([
            Transaction.type == "expense",
            Transaction.transaction_date >= month_start,
        ])

        budget_result = await db.execute(
            select(Budget).where(
                Budget.user_id == user_id,
                Budget.is_deleted == False,
            )
        )
        budgets = budget_result.scalars().all()
        budget_info = []
        for b in budgets:
            cat_result = await db.execute(
                select(Category).where(Category.id == b.category_id)
            )
            cat = cat_result.scalar_one_or_none()
            budget_info.append({
                "category": cat.name if cat else "未分类",
                "total": float(b.limit_amount),
                "spent": float(await _sum_amount([
                    Transaction.type == "expense",
                    Transaction.category_id == b.category_id,
                    Transaction.transaction_date >= month_start,
                ])),
            })

        recent_result = await db.execute(
            select(Transaction)
            .where(Transaction.user_id == user_id, Transaction.is_deleted == False)
            .order_by(Transaction.transaction_date.desc())
            .limit(5)
        )
        recent = recent_result.scalars().all()
        recent_list = []
        for tx in recent:
            cat_name = "未分类"
            if tx.category_id:
                cat_result = await db.execute(
                    select(Category).where(Category.id == tx.category_id)
                )
                cat = cat_result.scalar_one_or_none()
                if cat:
                    cat_name = cat.name
            recent_list.append({
                "date": tx.transaction_date.isoformat() if tx.transaction_date else "",
                "type": tx.type,
                "amount": float(tx.amount),
                "category": cat_name,
                "remark": tx.remark or "",
            })

        return {
            "today": {"income": today_income, "expense": today_expense},
            "this_week": {"income": week_income, "expense": week_expense},
            "this_month": {"income": month_income, "expense": month_expense},
            "budgets": budget_info,
            "recent_transactions": recent_list,
        }

    def _build_system_prompt(self, context: Dict) -> str:
        ctx_json = json.dumps(context, ensure_ascii=False, indent=2)
        today = datetime.now().strftime("%Y-%m-%d")
        return (
            f'你是一个智能记账助手，名叫"CoinWise AI"。'
            f"帮助用户管理个人财务。\n\n"
            f"## 用户实时财务数据（{today}）\n"
            f"```json\n{ctx_json}\n```\n\n"
            f"## 能力\n"
            f'1. 回答收支问题：根据上面的实时数据回答"今天/这周/这个月花了多少"\n'
            f"2. 帮用户记账：从用户消息中提取金额、分类、描述，返回结构化指令\n"
            f"3. 分析消费习惯：基于数据给出建议\n"
            f"4. 预算提醒：如果某分类预算快超支，主动提醒\n\n"
            f"## 记账指令格式\n"
            f'当用户说"记一笔午餐20元"时，在回复末尾附加 JSON 指令：\n\n'
            f"[ACTION:CREATE_TRANSACTION]\n"
            f'{{"amount":20,"type":"expense","category_name":"餐饮","remark":"午餐",'
            f'"transaction_date":"{today}"}}\n'
            f"[/ACTION]\n\n"
            f"## 查询指令格式\n"
            f'当用户问"这周花了多少"时，在回复末尾附加：\n\n'
            f"[ACTION:QUERY]\n"
            f'{{"type":"expense","period":"week"}}\n'
            f"[/ACTION]\n\n"
            f"## 规则\n"
            f"- 回复简洁、口语化，用中文\n"
            f"- 金额保留两位小数\n"
            f"- 如果用户没指定分类，根据描述智能推断\n"
            f'- 如果数据中没有，诚实说"暂无记录"\n'
            f"- 不要编造数据，只用实时数据"
        )

    def _parse_action(self, ai_reply: str) -> Optional[Dict]:
        pattern = r'\[ACTION:(\w+)\]\s*(.*?)\s*\[/ACTION\]'
        matches = re.findall(pattern, ai_reply, re.DOTALL)
        if not matches:
            return None
        action_type, action_json = matches[-1]
        try:
            data = json.loads(action_json.strip())
            data["action_type"] = action_type
            return data
        except json.JSONDecodeError:
            return None

    def _fallback_parse(self, message: str) -> Optional[Dict]:
        amount_match = re.search(r'(\d+\.?\d*)\s*(?:元|块)', message)
        if not amount_match:
            return None

        amount = float(amount_match.group(1))
        is_income = any(w in message for w in ["工资", "收入", "到账", "赚了", "收到", "退款"])
        tx_type = "income" if is_income else "expense"

        keywords = {
            "餐饮": ["饭", "餐", "吃", "午餐", "晚餐", "早餐", "外卖", "奶茶", "咖啡", "面包", "超市", "买菜"],
            "交通": ["地铁", "公交", "打车", "滴滴", "出租车", "加油", "停车", "高铁"],
            "购物": ["买", "淘宝", "京东", "衣服", "鞋", "包", "手机"],
            "住房": ["房租", "房贷", "物业", "水电", "燃气", "宽带"],
            "娱乐": ["电影", "游戏", "KTV", "旅游", "门票", "会员"],
            "医疗": ["医院", "药", "诊所", "体检", "挂号"],
            "教育": ["学费", "书", "课程", "培训", "考试", "学习"],
        }
        category_name = "未分类"
        for cat, kws in keywords.items():
            if any(kw in message for kw in kws):
                category_name = cat
                break

        remark = message.replace(amount_match.group(0), "").strip()
        return {
            "action_type": "CREATE_TRANSACTION",
            "amount": amount,
            "type": tx_type,
            "category_name": category_name,
            "remark": remark or category_name,
            "transaction_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        }
