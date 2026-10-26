from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status, Response
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db, get_write_db, get_current_user
from models.user import User
from services.import_export import parse_csv, parse_ofx, export_csv
from repositories.transaction import TransactionRepository

router = APIRouter()


@router.post("/import", summary="导入 CSV/OFX 文件")
async def import_file(
    file: UploadFile = File(...),
    account_id: int = Query(..., description="目标账户ID"),
    db: AsyncSession = Depends(get_write_db),
    current_user: User = Depends(get_current_user),
):
    content = (await file.read()).decode("utf-8", errors="replace")
    filename = file.filename.lower() if file.filename else ""

    if filename.endswith(".csv"):
        transactions = parse_csv(content, current_user.id, account_id)
    elif filename.endswith(".ofx") or filename.endswith(".qfx"):
        transactions = parse_ofx(content, current_user.id, account_id)
    else:
        raise HTTPException(status_code=400, detail="仅支持 CSV 和 OFX 格式")

    repo = TransactionRepository(db)
    imported = 0
    skipped = 0
    for tx in transactions:
        try:
            await repo.create(tx)
            imported += 1
        except Exception:
            skipped += 1

    if imported > 0:
        await db.commit()

    return {
        "imported": imported,
        "skipped": skipped,
        "message": f"成功导入 {imported} 条，跳过 {skipped} 条",
    }


@router.get("/export", summary="导出交易记录为 CSV")
async def export_file(
    start_date: str = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(None, description="结束日期 YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from datetime import datetime
    repo = TransactionRepository(db)
    filters = {}
    if start_date:
        filters["start_date"] = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date:
        filters["end_date"] = datetime.strptime(end_date, "%Y-%m-%d")
    transactions, total = await repo.list_by_user(
        user_id=current_user.id, **filters, limit=10000
    )
    csv_content = export_csv(transactions)

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=coinwise_export.csv"},
    )
