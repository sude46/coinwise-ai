"""审计中间件

记录所有非 GET 请求到审计日志（通过 Celery 异步写入），
不阻塞业务接口响应。
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from infrastructure.factory import get_celery


class AuditMiddleware(BaseHTTPMiddleware):
    """审计日志中间件：记录所有 POST/PUT/DELETE 等变更操作"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # 只记录变更操作（GET/HEAD/OPTIONS 不记录）
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return response

        # 只记录 API 请求
        if not request.url.path.startswith("/api/"):
            return response

        try:
            celery_app = get_celery()
            user_id = getattr(request.state, "user_id", None)
            celery_app.send_task(
                "tasks.audit_tasks.write_audit_log",
                kwargs={
                    "user_id": user_id,
                    "action": f"{request.method}_{request.url.path}",
                    "resource": request.url.path.split("/")[3] if len(request.url.path.split("/")) > 3 else "unknown",
                    "ip_address": request.client.host if request.client else None,
                    "user_agent": request.headers.get("user-agent"),
                    "request_id": request.headers.get("x-request-id"),
                },
            )
        except Exception:
            # 审计失败不影响主流程
            pass

        return response


def setup_audit_middleware(app):
    app.add_middleware(AuditMiddleware)
