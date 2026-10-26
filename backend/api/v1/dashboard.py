"""仪表盘聚合数据"""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db, get_current_user
from services.dashboard import DashboardService
from models.user import User

router = APIRouter()


@router.get("")
async def get_dashboard(
    year_month: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """仪表盘聚合接口"""
    if year_month is None:
        year_month = datetime.utcnow().strftime("%Y-%m")

    service = DashboardService(db)
    return await service.get_dashboard(current_user.id, year_month)
