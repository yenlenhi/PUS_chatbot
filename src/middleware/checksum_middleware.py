"""
Checksum verification middleware for data integrity
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import hashlib
import os


class ChecksumMiddleware(BaseHTTPMiddleware):
    """
    Middleware to verify checksum for data integrity
    Expects 'X-Checksum' and 'X-Checksum-Algorithm' headers
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.enable_checksum = (
            os.getenv("ENABLE_CHECKSUM_VERIFICATION", "false").lower() == "true"
        )
        self.checksum_required_paths = [
            "/api/admin/upload",
            "/api/documents/upload",
        ]

    async def dispatch(self, request: Request, call_next):
        """Verify checksum if enabled and required for the path"""
        if self.enable_checksum and any(
            request.url.path.startswith(path) for path in self.checksum_required_paths
        ):
            # Check if checksum headers are present
            checksum_header = request.headers.get("X-Checksum")
            algorithm_header = request.headers.get("X-Checksum-Algorithm", "sha256")

            if checksum_header:
                # Read request body
                body = await request.body()

                # Calculate checksum
                calculated_checksum = self._calculate_checksum(body, algorithm_header)

                # Verify checksum
                if calculated_checksum != checksum_header.lower():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Checksum verification failed. Data integrity compromised.",
                    )

                # Create new request with body

                scope = request.scope
                scope["body"] = body

                request = Request(scope, receive=request.receive)

        response = await call_next(request)
        return response

    def _calculate_checksum(self, data: bytes, algorithm: str = "sha256") -> str:
        """
        Calculate checksum for data

        Args:
            data: Data bytes
            algorithm: Hash algorithm (md5 or sha256)

        Returns:
            Checksum hex string
        """
        if algorithm.lower() == "md5":
            return hashlib.md5(data).hexdigest()
        elif algorithm.lower() == "sha256":
            return hashlib.sha256(data).hexdigest()
        else:
            raise ValueError(f"Unsupported checksum algorithm: {algorithm}")
