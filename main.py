"""
Main FastAPI application for University Chatbot
"""

from dotenv import load_dotenv

# Load environment variables from .env file at the very beginning
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pathlib import Path
import time
import uvicorn
from src.api.routes import router
from src.api.auth_routes import auth_router
from src.api.user_routes import user_router
from src.api.thammuu_routes import router as thammuu_router
from src.middleware.https_middleware import (
    HTTPSRedirectMiddleware,
    SecurityHeadersMiddleware,
)
from src.middleware.checksum_middleware import ChecksumMiddleware
from src.middleware.rate_limit_middleware import (
    RateLimitMiddleware,
    custom_rate_limit_exceeded_handler,
)
from slowapi.errors import RateLimitExceeded
from src.utils.logger import log
from config.settings import (
    API_HOST,
    API_PORT,
    API_RELOAD,
    ALLOWED_ORIGINS,
    PDF_DIR,
    BASE_DIR,
)
import shutil

from contextlib import asynccontextmanager


# Create FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    log.info("Starting University Chatbot API...")
    log.info(f"API documentation available at: http://{API_HOST}:{API_PORT}/docs")

    # Initialize async services
    try:
        from src.services.async_postgres_database_service import (
            get_async_database_service,
        )
        from src.services.async_user_service import get_async_user_service

        # Initialize database service
        log.info("Initializing async database service...")
        await get_async_database_service()

        # Initialize user service
        log.info("Initializing async user service...")
        await get_async_user_service()

        log.info("✅ Async services initialized successfully")
    except Exception as e:
        log.error(f"❌ Failed to initialize async services: {e}")
        # Don't crash the server, continue with sync fallback
    try:
        repo_pdfs = BASE_DIR / "data" / "pdfs"
        target_pdfs = Path(PDF_DIR)
        target_pdfs.mkdir(parents=True, exist_ok=True)

        # If target is empty but repo has files, copy them into the volume
        if (
            repo_pdfs.exists()
            and any(repo_pdfs.iterdir())
            and not any(target_pdfs.iterdir())
        ):
            files_copied = 0
            for src in repo_pdfs.rglob("*"):
                if src.is_file():
                    rel = src.relative_to(repo_pdfs)
                    dest = target_pdfs / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dest)
                    files_copied += 1
            log.info(
                f"Copied {files_copied} PDF files from bundled repo to data volume: {target_pdfs}"
            )
    except Exception as e:
        log.warning(f"Failed to copy bundled PDFs to data volume: {e}")
    yield
    # Shutdown logic
    log.info("Shutting down University Chatbot API...")

    # Close async database connections
    try:
        from src.services.async_postgres_database_service import _async_db_service

        if _async_db_service:
            await _async_db_service.close()
            log.info("✅ Async database service closed")
    except Exception as e:
        log.warning(f"⚠️ Error closing async database service: {e}")


app = FastAPI(
    title="University Chatbot API",
    description="API for university information chatbot with RAG capabilities",
    version="1.0.0",
    lifespan=lifespan,
)

# Add Security Middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(ChecksumMiddleware)
app.add_middleware(RateLimitMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Configure in settings
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = time.time()

    # Log request
    log.info(f"Request: {request.method} {request.url}")

    # Process request
    response = await call_next(request)

    # Log response
    process_time = time.time() - start_time
    log.info(f"Response: {response.status_code} - {process_time:.3f}s")

    return response


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    log.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": "Dữ liệu đầu vào không hợp lệ", "errors": exc.errors()},
    )


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors"""
    return custom_rate_limit_exceeded_handler(request, exc)


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    log.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Đã xảy ra lỗi hệ thống. Vui lòng thử lại sau."},
    )


# Include routes
app.include_router(auth_router, prefix="/api/v1")
app.include_router(user_router)  # Already has /api/users prefix
app.include_router(router, prefix="/api/v1")
app.include_router(thammuu_router, prefix="/api/v1")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "University Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# Health check endpoint (for Railway)
@app.get("/health")
async def health_check():
    """Health check endpoint for Railway deployment"""
    return {
        "status": "healthy",
        "service": "University Chatbot API",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import os

    # Support Railway PORT environment variable
    port = int(os.environ.get("PORT", API_PORT))
    host = os.environ.get("HOST", API_HOST)

    # Run the application
    uvicorn.run("main:app", host=host, port=port, reload=API_RELOAD, log_level="info")
