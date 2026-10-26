"""AI 月度报告"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db, get_current_user
from schemas.monthly_report import MonthlyReportOut
from services.report import ReportService
from models.user import User

router = APIRouter()


@router.get("/{year_month}", response_model=MonthlyReportOut)
async def get_report(
    year_month: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取或生成月度报告（factory context manager 自动 commit）"""
    service = ReportService(db)
    report = await service.get_or_generate_report(current_user.id, year_month)
    return report


@router.get("", response_model=List[MonthlyReportOut])
async def list_reports(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取报告列表"""
    service = ReportService(db)
    return await service.list_reports(current_user.id)
