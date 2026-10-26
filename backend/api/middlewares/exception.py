"""全局异常统一 JSON 响应中间件

捕获所有未处理的异常，统一输出结构化 JSON，避免堆栈信息泄露到前端。
"""

import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from core.exceptions import BusinessException, UnauthorizedException, ForbiddenException, NotFoundException

logger = logging.getLogger(__name__)


class ExceptionMiddleware(BaseHTTPMiddleware):
    """全局异常统一处理中间件"""

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except (UnauthorizedException, ForbiddenException, NotFoundException, BusinessException) as exc:
            # 已知业务异常，直接返回
            return JSONResponse(
                status_code=exc.status_code,
                content={"code": exc.status_code, "message": exc.detail, "data": None},
            )
        except Exception as exc:
            # 未知异常，记录日志，返回通用错误（不暴露堆栈）
            logger.exception(f"Unhandled exception at {request.method} {request.url.path}: {exc}")
            return JSONResponse(
                status_code=500,
                content={"code": 500, "message": "服务器内部错误", "data": None},
            )


def setup_exception_middleware(app):
    app.add_middleware(ExceptionMiddleware)
