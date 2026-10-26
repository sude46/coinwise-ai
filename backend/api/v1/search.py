"""全文检索接口 — 基于 MySQL FULLTEXT + ngram 分词

文档明确删除 ES（过度设计），改用 MySQL 8.0 内置 FULLTEXT，
支持中文分词（ngram 解析器），零额外组件。

建表时需已执行：
    ALTER TABLE transactions
    ADD FULLTEXT INDEX ft_remark (remark) WITH PARSER ngram;
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, text, func
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db, get_current_user
from models.user import User
from models.transaction import Transaction
from models.category import Category

router = APIRouter()


@router.get("")
async def search_transactions(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    category_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """全文检索流水记录（基于 MySQL FULLTEXT）"""
    offset = (page - 1) * size

    # 基础查询条件
    base_conditions = [
        Transaction.user_id == current_user.id,
        Transaction.is_deleted == False,
    ]
    if category_id is not None:
        base_conditions.append(Transaction.category_id == category_id)

    # FULLTEXT 查询（MATCH ... AGAINST）
    # 注意：SQLAlchemy 原生不支持 MATCH，使用 text 片段
    match_expr = text("MATCH(transactions.remark) AGAINST (:q IN NATURAL LANGUAGE MODE)")

    count_query = (
        select(func.count(Transaction.id))
        .where(*base_conditions)
        .where(match_expr)
    )

    data_query = (
        select(Transaction, Category.name.label("category_name"))
        .join(Category, Transaction.category_id == Category.id, isouter=True)
        .where(*base_conditions)
        .where(match_expr)
        .order_by(Transaction.transaction_date.desc())
        .offset(offset)
        .limit(size)
    )

    try:
        total_result = await db.execute(count_query, {"q": q})
        total = total_result.scalar() or 0

        result = await db.execute(data_query, {"q": q})
        rows = result.all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索服务异常: {e}")

    items = []
    for tx, cat_name in rows:
        items.append({
            "id": tx.id,
            "remark": tx.remark,
            "amount": float(tx.amount),
            "transaction_date": tx.transaction_date.isoformat() if tx.transaction_date else None,
            "category_name": cat_name or "",
            "type": tx.type,
        })

    return {
        "total": total,
        "items": items,
        "page": page,
        "size": size,
    }
