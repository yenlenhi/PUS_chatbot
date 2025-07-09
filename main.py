"""
Main FastAPI application for University Chatbot
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import time
import uvicorn
from src.api.routes import router
from src.utils.logger import log
from config.settings import API_HOST, API_PORT, API_RELOAD
from contextlib import asynccontextmanager

# Create FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    log.info("Starting University Chatbot API...")
    log.info(f"API documentation available at: http://{API_HOST}:{API_PORT}/docs")
    yield
    # Shutdown logic
    log.info("Shutting down University Chatbot API...")

app = FastAPI(
    title="University Chatbot API",
    description="API for university information chatbot with RAG capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
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
        content={
            "detail": "Dữ liệu đầu vào không hợp lệ",
            "errors": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    log.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Đã xảy ra lỗi hệ thống. Vui lòng thử lại sau."
        }
    )


# Include routes
app.include_router(router, prefix="/api/v1")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "University Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host=API_HOST,
        port=API_PORT,
        reload=API_RELOAD,
        log_level="info"
    )

