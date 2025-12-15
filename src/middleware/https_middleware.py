"""
HTTPS and Security Headers Middleware
"""

from fastapi import Request, Response
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import os


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """
    Middleware to redirect HTTP requests to HTTPS
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.enforce_https = os.getenv("HTTPS_ONLY", "false").lower() == "true"

    async def dispatch(self, request: Request, call_next):
        """Redirect HTTP to HTTPS if enabled"""
        if self.enforce_https:
            # Check if request is not already HTTPS
            if request.url.scheme != "https":
                # Check for X-Forwarded-Proto header (for reverse proxies)
                forwarded_proto = request.headers.get("X-Forwarded-Proto")
                if forwarded_proto != "https":
                    # Redirect to HTTPS
                    url = request.url.replace(scheme="https")
                    return RedirectResponse(url=str(url), status_code=301)

        response = await call_next(request)
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to responses
    """

    async def dispatch(self, request: Request, call_next):
        """Add security headers to response"""
        response: Response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'"
        )

        # Require TLS 1.2 or higher (informational header)
        response.headers["X-Min-TLS-Version"] = "1.2"

        return response
