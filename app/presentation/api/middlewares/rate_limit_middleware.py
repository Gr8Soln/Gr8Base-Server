from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import Settings
from app.core.utils import error_response
from app.infrastructure.services.rate_limiter_service import (
    RedisRateLimiterService,
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, cache_service, settings: Settings) -> None:
        super().__init__(app)
        self._rate_limiter = RedisRateLimiterService(cache_service, settings)

    async def dispatch(self, request: Request, call_next):
        decision = await self._rate_limiter.check_request(request)
        if decision is not None and not decision.allowed:
            retry_after = max(decision.window_seconds, 1)
            response = error_response(
                "RATE_LIMIT_EXCEEDED",
                data={
                    "rule": decision.rule_name,
                    "limit": decision.limit,
                    "window_seconds": decision.window_seconds,
                    "current_count": decision.current_count,
                    "identity_scope": decision.identity_scope,
                },
            )
            return JSONResponse(
                status_code=429,
                content=response.model_dump(mode="json"),
                headers={"Retry-After": str(retry_after)},
            )

        return await call_next(request)
