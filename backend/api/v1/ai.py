"""AI 助手对话接口

使用阿里云百炼实现智能对话（无条件则降级为规则 Agent）。
"""

import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db
from schemas.ai import AIChatRequest
from models.user import User
from models.transaction import Transaction
from models.category import Category
from core.config import settings
from infrastructure.factory import get_celery

router = APIRouter(tags=["AI 助手"])


def _sanitize_html(raw: str) -> str:
    raw = re.sub(r"<script[^>]*>.*?</script>", "", raw, flags=re.S | re.I)
    raw = re.sub(r"<style[^>]*>.*?</style>", "", raw, flags=re.S | re.I)
    raw = re.sub(r"\s*on\w+\s*=\s*['\"][^'\"]*['\"]", "", raw, flags=re.I)
    raw = re.sub(r"javascript:", "", raw, flags=re.I)
    return raw


conversation_store: dict = {}


@router.post("/chat")
async def ai_chat(
    payload: AIChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if settings.BAILIAN_API_KEY:
        return await _bailian_chat(payload, db, current_user)

    return await _agent_chat(payload, current_user)


async def _bailian_chat(
    payload: AIChatRequest,
    db: AsyncSession,
    current_user: User,
):
    from services.bailian_service import BailianService

    service = BailianService()
    history = conversation_store.get(f"{current_user.id}:{payload.conversation_id}", []) if payload.conversation_id else []

    result = await service.chat(
        message=payload.text,
        user_id=current_user.id,
        db=db,
        conversation_history=history,
    )

    action_feedback = None
    if result.get("action"):
        action_feedback = await _execute_action(result["action"], current_user.id, db)

    reply = result["reply"]
    if action_feedback and action_feedback not in reply:
        reply += f"\n\n{action_feedback}"

    if result.get("error"):
        return {
            "type": "text",
            "content": _sanitize_html(reply),
            "action": None,
            "usage": None,
        }

    if payload.conversation_id:
        history.append({"role": "user", "content": payload.text})
        history.append({"role": "assistant", "content": reply})
        conversation_store[f"{current_user.id}:{payload.conversation_id}"] = history[-10:]

    return {
        "type": "text",
        "content": _sanitize_html(reply),
        "action": result.get("action"),
        "usage": result.get("usage"),
    }


async def _agent_chat(payload: AIChatRequest, current_user: User):
    from agents.nl_transaction import NLTransactionAgent
    from agents.finance_strategy import FinanceStrategyAgent
    from agents.anomaly import AnomalyAgent

    intent = payload.intent
    text = payload.text

    if intent == "bookkeeping":
        agent = NLTransactionAgent()
        result = await agent.execute({"text": text, "user_id": current_user.id})
        if result.get("success"):
            parsed = result.get("parsed_data", {})
            if "remark" in parsed:
                parsed["remark"] = _sanitize_html(parsed["remark"])
            return {"type": "transaction_confirm", "parsed_data": parsed, "needs_confirm": True}
        return {"type": "text", "content": "未能理解您的记账意图，请尝试用「金额+用途」格式描述。"}

    elif intent == "strategy":
        agent = FinanceStrategyAgent()
        result = await agent.execute({**payload.model_dump(), "user_id": current_user.id})
        return {"type": "text", "content": _sanitize_html(result.get("message", ""))}

    elif intent == "anomaly_check":
        from sqlalchemy import select
        from datetime import datetime, timedelta
        from models.transaction import Transaction
        from models.category import Category

        recent_txs = []
        tx_result = await db.execute(
            select(Transaction, Category.name.label("cat_name"))
            .outerjoin(Category, Transaction.category_id == Category.id)
            .where(
                Transaction.user_id == current_user.id,
                Transaction.is_deleted == False,
            )
            .order_by(Transaction.transaction_date.desc())
            .limit(50)
        )
        for tx_row, cat_name in tx_result.all():
            tx_date = tx_row.transaction_date
            h = tx_date.hour if hasattr(tx_date, "hour") else 0
            recent_txs.append({
                "id": tx_row.id,
                "amount": float(tx_row.amount),
                "type": tx_row.type,
                "category_name": cat_name or "未分类",
                "category_id": tx_row.category_id,
                "transaction_date": tx_date.isoformat() if tx_date else None,
            })

        agent = AnomalyAgent()
        result = await agent.execute({"transactions": recent_txs})
        if result.get("has_anomaly"):
            alerts = result.get("alerts", [])
            content = "\n\n".join([a["message"] for a in alerts])
        else:
            content = "近期消费未发现明显异常。"
        return {"type": "text", "content": _sanitize_html(content)}

    elif intent == "report":
        celery_app = get_celery()
        celery_app.send_task("tasks.report_tasks.generate_monthly_report", args=[current_user.id])
        return {"type": "text", "content": "正在为您生成月度报告，请稍后在「报表」页面查看。"}

    else:
        return {"type": "text", "content": "暂时不支持该意图，请尝试「记账」「策略」「异常检测」等。"}


async def _execute_action(action: dict, user_id: int, db: AsyncSession):
    from sqlalchemy import select, func
    from datetime import datetime, timezone, timedelta
    from decimal import Decimal

    action_type = action.get("action_type")

    if action_type == "CREATE_TRANSACTION":
        from models.transaction import Transaction as TxModel
        from schemas.transaction import TransactionCreate
        from services.transaction import TransactionService

        category_name = action.get("category_name", "未分类")
        cat_result = await db.execute(
            select(Category).where(Category.user_id == user_id, Category.name == category_name)
        )
        category = cat_result.scalar_one_or_none()

        now_utc = datetime.now(timezone.utc)
        date_str = action.get("transaction_date") or now_utc.strftime("%Y-%m-%d")
        try:
            tx_date = datetime.fromisoformat(date_str)
        except ValueError:
            date_str = now_utc.strftime("%Y-%m-%d")
            tx_date = datetime.fromisoformat(date_str)
        # LLM 可能只返回日期没带时间，补上当前时间
        if 'T' not in date_str:
            tx_date = tx_date.replace(
                hour=now_utc.hour,
                minute=now_utc.minute,
                second=now_utc.second,
            )

        tx_data = TransactionCreate(
            amount=Decimal(str(action["amount"])),
            type=action["type"],
            category_id=category.id if category else None,
            remark=action.get("remark", ""),
            transaction_date=tx_date,
            source="ai",
        )
        service = TransactionService(db)
        await service.create_transaction(user_id, tx_data)

        type_str = "支出" if action["type"] == "expense" else "收入"
        return f"✅ 已记账：{type_str} ¥{action['amount']} - {category_name}"

    elif action_type == "QUERY":
        period = action.get("period", "week")
        now = datetime.utcnow()
        if period == "today":
            start = now.replace(hour=0, minute=0, second=0)
        elif period == "week":
            start = now - timedelta(days=7)
        elif period == "month":
            start = now.replace(day=1, hour=0, minute=0, second=0)
        else:
            start = now - timedelta(days=30)

        stmt = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.user_id == user_id,
            Transaction.type == action.get("type", "expense"),
            Transaction.transaction_date >= start,
            Transaction.is_deleted == False,
        )
        result = await db.execute(stmt)
        total = float(result.scalar() or 0)

        type_str = "支出" if action.get("type", "expense") == "expense" else "收入"
        period_map = {"today": "今天", "week": "近7天", "month": "本月"}
        return f"📊 查询结果：{period_map.get(period, '近30天')}共{type_str} ¥{total:.2f}"

    return None
