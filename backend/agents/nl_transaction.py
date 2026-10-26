"""NLTransactionAgent — 自然语言记账 Agent

解析用户输入（如"中午吃了碗面15块"）为结构化流水数据，
返回确认卡片格式供前端渲染。
"""

import re
from typing import Optional
from decimal import Decimal

from agents.base import BaseAgent


class NLTransactionAgent(BaseAgent):
    """自然语言记账解析 Agent"""

    async def execute(self, payload: dict) -> dict:
        raw_text = payload.get("text", "")
        if not raw_text:
            return {"success": False, "error": "空输入"}

        # 1. 金额提取（支持 "15块"、"¥20.5"、"100元"）
        amount = self._extract_amount(raw_text)
        # 2. 类型推断（收入/支出关键词）
        tx_type = self._infer_type(raw_text)
        # 3. 分类提示（基于关键词映射）
        category_hint = self._infer_category(raw_text)
        # 4. 备注清理
        remark = self._clean_remark(raw_text)

        if amount is None:
            return {"success": False, "error": "未能识别金额", "raw": raw_text}

        return {
            "success": True,
            "type": "transaction_confirm",
            "parsed_data": {
                "type": tx_type,
                "amount": float(amount),
                "category_hint": category_hint,
                "remark": remark,
            },
            "needs_confirm": True,
        }

    def _extract_amount(self, text: str) -> Optional[Decimal]:
        patterns = [
            r"(\d+(?:\.\d{1,2})?)\s*(?:元|块|¥|￥)",
            r"[¥￥]\s*(\d+(?:\.\d{1,2})?)",
        ]
        for pat in patterns:
            m = re.search(pat, text)
            if m:
                return Decimal(m.group(1))
        return None

    def _infer_type(self, text: str) -> str:
        income_keywords = {"工资", "奖金", "收入", "红包", "退款", "收益"}
        if any(kw in text for kw in income_keywords):
            return "income"
        return "expense"

    def _infer_category(self, text: str) -> str:
        mapping = {
            "餐饮": {"吃", "饭", "面", "奶茶", "咖啡", "餐厅", "外卖", "火锅", "烧烤"},
            "交通": {"地铁", "公交", "打车", "滴滴", "加油", "高铁", "飞机"},
            "购物": {"买", "淘宝", "京东", "超市", "衣服", "鞋", "包"},
            "娱乐": {"电影", "游戏", "KTV", "演唱会", "旅游", "门票"},
            "住房": {"房租", "房贷", "物业", "水电", "燃气"},
            "医疗": {"药", "医院", "挂号", "体检", "诊所"},
        }
        for cat, kws in mapping.items():
            if any(kw in text for kw in kws):
                return cat
        return "其他"

    def _clean_remark(self, text: str) -> str:
        # 移除金额标记，保留语义
        cleaned = re.sub(r"(\d+(?:\.\d{1,2})?)\s*(?:元|块|¥|￥)", "", text)
        cleaned = re.sub(r"[，,。\.]+$", "", cleaned).strip()
        return cleaned or text
