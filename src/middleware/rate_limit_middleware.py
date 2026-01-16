"""
Rate Limiting Middleware for University Chatbot
Protects sensitive endpoints from DDoS and brute force attacks
"""

import time
import hashlib
from typing import Optional
from fastapi import Request
from fastapi.responses import JSONResponse
import redis
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from config.settings import REDIS_URL, RATE_LIMIT_ENABLED
from src.utils.logger import log


# Initialize Redis connection for rate limiting
try:
    if REDIS_URL:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        redis_client.ping()
        log.info("✅ Redis connected successfully for rate limiting")
    else:
        log.warning("⚠️ No REDIS_URL configured, using in-memory fallback")
        redis_client = None
except Exception as e:
    log.warning(f"⚠️ Redis connection failed, using in-memory fallback: {e}")
    redis_client = None


# Fallback in-memory storage when Redis is not available
class InMemoryStorage:
    def __init__(self):
        self._storage = {}

    def get(self, key: str) -> Optional[str]:
        entry = self._storage.get(key)
        if entry and entry["expires"] > time.time():
            return entry["value"]
        elif entry:
            del self._storage[key]
        return None

    def set(self, key: str, value: str, ex: int = None):
        expires = time.time() + ex if ex else float("inf")
        self._storage[key] = {"value": value, "expires": expires}

    def incr(self, key: str) -> int:
        current = self.get(key)
        new_value = int(current or 0) + 1
        self.set(key, str(new_value), ex=60)  # Default 1 minute expiry
        return new_value


# Use Redis or fallback to in-memory storage
storage = redis_client if redis_client else InMemoryStorage()


def get_identifier(request: Request) -> str:
    """
    Get unique identifier for rate limiting
    Combines IP address and User-Agent for better accuracy
    """
    ip = get_remote_address(request)
    user_agent = request.headers.get("User-Agent", "")

    # Create hash of IP + User-Agent for privacy
    identifier_data = f"{ip}:{user_agent}"
    identifier_hash = hashlib.sha256(identifier_data.encode()).hexdigest()[:16]

    return identifier_hash


# Create limiter instance
limiter = Limiter(
    key_func=get_identifier,
    storage_uri=REDIS_URL if redis_client else "memory://",
    enabled=RATE_LIMIT_ENABLED,
)


class RateLimitMiddleware:
    """
    Enhanced Rate Limiting Middleware with different limits for different endpoints
    """

    # Define rate limits for different endpoint patterns
    ENDPOINT_LIMITS = {
        "/api/auth/login": "5/minute",  # Login attempts
        "/api/auth/register": "3/minute",  # Registration attempts
        "/api/auth/": "10/minute",  # General auth endpoints
        "/api/admin/": "30/minute",  # Admin endpoints
        "/api/chat": "60/minute",  # Chat endpoint
        "/api/upload": "10/minute",  # File upload
        "default": "120/minute",  # Default for other endpoints
    }

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)

        # Skip rate limiting for health checks and static files
        if self._should_skip_rate_limit(request):
            await self.app(scope, receive, send)
            return

        # Apply rate limiting
        try:
            await self._check_rate_limit(request)
            await self.app(scope, receive, send)
        except RateLimitExceeded as e:
            response = JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": "Quá nhiều request. Vui lòng thử lại sau.",
                    "retry_after": getattr(e, "retry_after", 60),
                    "detail": str(e),
                },
            )
            await response(scope, receive, send)
        except Exception as e:
            log.error(f"Rate limiting error: {e}")
            # Continue with request if rate limiting fails
            await self.app(scope, receive, send)

    def _should_skip_rate_limit(self, request: Request) -> bool:
        """Check if request should skip rate limiting"""
        path = request.url.path

        # Skip for health checks, static files, docs
        skip_patterns = [
            "/health",
            "/docs",
            "/openapi.json",
            "/favicon.ico",
            "/static/",
            "/assets/",
            "/.well-known/",
        ]

        return any(path.startswith(pattern) for pattern in skip_patterns)

    async def _check_rate_limit(self, request: Request):
        """Check and enforce rate limits based on endpoint"""
        if not RATE_LIMIT_ENABLED:
            return

        path = request.url.path
        method = request.method
        identifier = get_identifier(request)

        # Determine rate limit for this endpoint
        limit_str = self._get_rate_limit_for_path(path)

        # Parse limit (e.g., "5/minute" -> 5 requests per 60 seconds)
        requests, period = self._parse_rate_limit(limit_str)
        window_seconds = self._get_window_seconds(period)

        # Create Redis key
        window_start = int(time.time() // window_seconds) * window_seconds
        rate_key = f"rate_limit:{identifier}:{path}:{method}:{window_start}"

        try:
            # Check current count
            if redis_client:
                current_count = redis_client.get(rate_key)
                current_count = int(current_count) if current_count else 0

                if current_count >= requests:
                    raise RateLimitExceeded(
                        f"Rate limit exceeded: {requests} requests per {period}"
                    )

                # Increment counter
                pipeline = redis_client.pipeline()
                pipeline.incr(rate_key)
                pipeline.expire(rate_key, window_seconds)
                pipeline.execute()

            else:
                # Fallback to in-memory
                current_count = storage.get(rate_key)
                current_count = int(current_count) if current_count else 0

                if current_count >= requests:
                    raise RateLimitExceeded(
                        f"Rate limit exceeded: {requests} requests per {period}"
                    )

                storage.set(rate_key, str(current_count + 1), window_seconds)

            # Log suspicious activity
            if current_count > requests * 0.8:  # Log when approaching limit
                log.warning(
                    f"High request rate from {identifier[:8]}... "
                    f"to {path}: {current_count + 1}/{requests} per {period}"
                )

        except RateLimitExceeded:
            # Log rate limit violation
            log.warning(
                f"Rate limit exceeded for {identifier[:8]}... "
                f"on {method} {path} - {requests} per {period}"
            )
            raise
        except Exception as e:
            log.error(f"Rate limiting check failed: {e}")
            # Don't block request if rate limiting fails
            return

    def _get_rate_limit_for_path(self, path: str) -> str:
        """Get rate limit configuration for specific path"""
        for pattern, limit in self.ENDPOINT_LIMITS.items():
            if path.startswith(pattern) and pattern != "default":
                return limit
        return self.ENDPOINT_LIMITS["default"]

    def _parse_rate_limit(self, limit_str: str) -> tuple:
        """Parse rate limit string like '5/minute' to (5, 'minute')"""
        parts = limit_str.split("/")
        return int(parts[0]), parts[1]

    def _get_window_seconds(self, period: str) -> int:
        """Convert period to seconds"""
        period_map = {"second": 1, "minute": 60, "hour": 3600, "day": 86400}
        return period_map.get(period, 60)


# Rate limiting decorator for specific endpoints
def rate_limit(limit_str: str):
    """
    Decorator for applying custom rate limits to specific endpoints
    Usage: @rate_limit("5/minute")
    """
    return limiter.limit(limit_str)


# Custom rate limit exceeded handler
def custom_rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded responses"""

    # Extract retry after from exception
    retry_after = getattr(exc, "retry_after", 60)

    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": "Quá nhiều request. Vui lòng thử lại sau.",
            "retry_after": retry_after,
            "detail": str(exc),
        },
        headers={"Retry-After": str(retry_after)},
    )
