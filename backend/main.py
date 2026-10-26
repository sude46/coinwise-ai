"""FastAPI 应用入口"""

from fastapi import FastAPI
from contextlib import asynccontextmanager

from api.v1 import auth, dashboard, transactions, categories, budgets, reports, search, accounts, savings_goals, ai, import_export
from middlewares.cors import setup_cors
from middlewares.rate_limit import setup_rate_limit
from api.middlewares.security import setup_security_headers
from api.middlewares.audit import setup_audit_middleware
from api.middlewares.exception import setup_exception_middleware
from infrastructure.db import Base, master_engine, slave_engine
from infrastructure.factory import close_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    import logging
    logger = logging.getLogger("lifespan")
    try:
        async with master_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database connected and tables synced")
    except Exception as e:
        logger.warning(f"Database connection failed: {e}. Application will continue without DB.")

    from services.notification import notification_service
    from core.config import settings as s
    if s.SMTP_HOST and s.SMTP_USER:
        notification_service.configure(s.SMTP_HOST, s.SMTP_PORT, s.SMTP_USER, s.SMTP_PASS)
        logger.info("Notification service configured with SMTP: %s", s.SMTP_HOST)

    yield
    for engine in [master_engine, slave_engine]:
        try:
            await engine.dispose()
        except Exception:
            pass
    try:
        await close_redis()
    except Exception:
        pass


app = FastAPI(
    title="CoinWise - 智能记账与财务分析平台",
    description="基于 FastAPI 与 Vue 的多层架构智能记账平台",
    version="1.0.0",
    lifespan=lifespan,
)

# 中间件（注意顺序：异常 → 安全头 → 审计 → 限流 → CORS）
setup_exception_middleware(app)
setup_security_headers(app)
setup_audit_middleware(app)
setup_rate_limit(app, rate=100, per=60)
setup_cors(app)

# API 路由
api_v1_prefix = "/api/v1"
app.include_router(auth.router, prefix=f"{api_v1_prefix}/auth", tags=["认证"])
app.include_router(dashboard.router, prefix=f"{api_v1_prefix}/dashboard", tags=["仪表盘"])
app.include_router(transactions.router, prefix=f"{api_v1_prefix}/transactions", tags=["记账"])
app.include_router(categories.router, prefix=f"{api_v1_prefix}/categories", tags=["分类"])
app.include_router(budgets.router, prefix=f"{api_v1_prefix}/budgets", tags=["预算"])
app.include_router(reports.router, prefix=f"{api_v1_prefix}/reports", tags=["报告"])
app.include_router(search.router, prefix=f"{api_v1_prefix}/search", tags=["搜索"])
app.include_router(accounts.router, prefix=f"{api_v1_prefix}/accounts", tags=["账户"])
app.include_router(savings_goals.router, prefix=f"{api_v1_prefix}/savings-goals", tags=["储蓄目标"])
app.include_router(ai.router, prefix=f"{api_v1_prefix}/ai", tags=["AI 助手"])
app.include_router(import_export.router, prefix=f"{api_v1_prefix}/import-export", tags=["导入导出"])




@app.get("/health")
async def health_check():
    return {"status": "ok"}
