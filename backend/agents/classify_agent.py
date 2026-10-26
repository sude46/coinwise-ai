"""智能分类 Agent"""

from agents.base import BaseAgent


class SmartCategoryAgent(BaseAgent):
    name = "classify"

    async def execute(self, payload: dict) -> dict:
        """
        根据备注内容智能推断分类。
        实际生产环境可接入 LLM API，此处为规则引擎示例。
        """
        remark = payload.get("remark", "")
        category_map = {
            "餐饮": ["餐厅", "饭店", "火锅", "烧烤", "咖啡", "奶茶", "星巴克", "肯德基", "麦当劳"],
            "交通": ["地铁", "公交", "打车", "出租车", "滴滴", "加油", "停车"],
            "购物": ["超市", "商场", "淘宝", "京东", "拼多多", "便利店"],
            "娱乐": ["电影", "KTV", "游戏", "旅游", "景点", "酒店"],
            "居住": ["房租", "水电", "物业", "宽带", "燃气"],
            "医疗": ["医院", "药店", "挂号", "体检"],
            "教育": ["学费", "书本", "培训", "课程", "考试"],
        }

        for category, keywords in category_map.items():
            for kw in keywords:
                if kw in remark:
                    return {
                        "transaction_id": payload.get("transaction_id"),
                        "suggested_category": category,
                        "confidence": 0.85,
                        "reason": f"备注中包含关键词 '{kw}'",
                    }

        return {
            "transaction_id": payload.get("transaction_id"),
            "suggested_category": "其他",
            "confidence": 0.5,
            "reason": "未匹配到明确分类",
        }
