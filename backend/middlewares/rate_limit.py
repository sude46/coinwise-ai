"""接口限流（Redis 漏斗算法）"""

import time
import logging
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from infrastructure.factory import get_redis

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """基于 Redis 的滑动窗口限流中间件（Redis 不可用时自动降级）"""

    def __init__(self, app, rate: int = 100, per: int = 60):
        super().__init__(app)
        self.rate = rate
        self.per = per
        self._redis_available = True

    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        if not self._redis_available:
            return await call_next(request)

        try:
            client_ip = request.client.host if request.client else "unknown"
            key = f"rate_limit:{client_ip}:{request.url.path}"

            redis_client = await get_redis()
            now = int(time.time())
            window_start = now - self.per

            await redis_client.zremrangebyscore(key, 0, window_start)
            current_count = await redis_client.zcard(key)
            if current_count >= self.rate:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="请求过于频繁，请稍后再试",
                )

            await redis_client.zadd(key, {str(now): now})
            await redis_client.expire(key, self.per)
        except HTTPException:
            raise
        except Exception as e:
            # Redis 不可用：记录一次警告，后续请求直接放行
            logger.warning(f"Redis rate limit failed: {e}. Disabling rate limit.")
            self._redis_available = False

        return await call_next(request)


def setup_rate_limit(app, rate: int = 100, per: int = 60):
    app.add_middleware(RateLimitMiddleware, rate=rate, per=per)
