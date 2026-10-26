"""安全响应头中间件

注入 CSP / HSTS / X-Content-Type-Options / X-Frame-Options 等响应头，
作为 Nginx 安全头的兜底补充（Nginx 负责传输层，这里负责应用层统一）。
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """统一安全响应头中间件"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # 防止 MIME 类型嗅探
        response.headers["X-Content-Type-Options"] = "nosniff"
        # 禁止页面被嵌入 iframe（点击劫持防护）
        response.headers["X-Frame-Options"] = "DENY"
        # XSS 过滤器（现代浏览器已弃用，但作为兜底）
        response.headers["X-XSS-Protection"] = "1; mode=block"
        #  Referrer 策略
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # 权限策略（限制浏览器 API）
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # CSP：限制资源加载来源（生产环境应收紧 script-src）
        # 注意：开发环境可能需要 'unsafe-inline' for style/script
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )

        return response


def setup_security_headers(app):
    app.add_middleware(SecurityHeadersMiddleware)
