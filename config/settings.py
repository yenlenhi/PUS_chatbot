"""
Configuration settings for the University Chatbot
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths - Support Railway Volume mount
BASE_DIR = Path(__file__).parent.parent

# Railway Volume: Mount tại /data, fallback về local data/ folder
# Set RAILWAY_VOLUME_MOUNT=/data trong Railway environment
VOLUME_MOUNT = os.getenv("RAILWAY_VOLUME_MOUNT", "")
if VOLUME_MOUNT:
    DATA_DIR = Path(VOLUME_MOUNT)
else:
    DATA_DIR = BASE_DIR / "data"

PDF_DIR = DATA_DIR / "pdfs"
NEW_PDF_DIR = DATA_DIR / "new_pdf"  # PDF scan directory
PROCESSED_DIR = DATA_DIR / "processed"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"

# Ensure directories exist
PDF_DIR.mkdir(parents=True, exist_ok=True)
NEW_PDF_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)


# LLM Provider Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # "ollama" or "gemini"

# Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = os.getenv(
    "GEMINI_API_URL",
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
)
GEMINI_MAX_OUTPUT_TOKENS = int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "8192"))
GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
# Enable/disable Gemini question normalization
ENABLE_GEMINI_NORMALIZATION = (
    os.getenv("ENABLE_GEMINI_NORMALIZATION", "true").lower() == "true"
)

# Ollama Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL", "llama3"
)  # Changed from myaniu/qwen2.5-1m for testing

# ============================================
# PostgreSQL Configuration (NEW)
# ============================================
POSTGRES_USER = os.getenv("POSTGRES_USER", "uni_bot_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "uni_bot_password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "uni_bot_db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))

# PostgreSQL Connection String
# Prefer Railway-provided URL when present, then explicit DATABASE_URL, then constructed local URL
RAILWAY_DATABASE_URL = os.getenv("RAILWAY_DATABASE_URL")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    RAILWAY_DATABASE_URL
    or f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}",
)

# Fix Railway's postgres:// URL scheme to postgresql:// for SQLAlchemy 1.4+
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ============================================
# Redis Configuration (NEW)
# ============================================
# Support Railway Redis URL format
REDIS_URL = os.getenv("REDIS_URL") or os.getenv("REDIS_PRIVATE_URL")

if REDIS_URL:
    # Parse Redis URL (format: redis://user:pass@host:port/db)
    import urllib.parse

    parsed = urllib.parse.urlparse(REDIS_URL)
    REDIS_HOST = parsed.hostname or "localhost"
    REDIS_PORT = parsed.port or 6379
    REDIS_PASSWORD = parsed.password
    REDIS_DB = int(parsed.path[1:]) if parsed.path and len(parsed.path) > 1 else 0
else:
    # Local fallback - read from individual env vars
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)  # None if no password

REDIS_DECODE_RESPONSES = os.getenv("REDIS_DECODE_RESPONSES", "false").lower() == "true"

# Redis Cache Configuration
REDIS_CACHE_TTL = int(os.getenv("REDIS_CACHE_TTL", "86400"))  # 24 hours default
REDIS_CACHE_PREFIX = os.getenv("REDIS_CACHE_PREFIX", "unibot:")
REDIS_EMBEDDING_PREFIX = os.getenv("REDIS_EMBEDDING_PREFIX", "emb:")

# Enable/disable Redis caching
ENABLE_REDIS_CACHE = os.getenv("ENABLE_REDIS_CACHE", "true").lower() == "true"

# ============================================
# Legacy Database Configuration (SQLite - for backward compatibility)
# ============================================
DATABASE_PATH = os.getenv("DATABASE_PATH", str(EMBEDDINGS_DIR / "chatbot.db"))
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", str(EMBEDDINGS_DIR / "faiss_index"))

# Embedding Model Configuration
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL", "bkai-foundation-models/vietnamese-embedding-v1"
)
BM25_INDEX_PATH = os.getenv("BM25_INDEX_PATH", str(EMBEDDINGS_DIR / "bm25_index.pkl"))

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_RELOAD = os.getenv("API_RELOAD", "True").lower() == "true"

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/chatbot.log")

# RAG Configuration
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "15"))
# Set a stricter threshold to filter out irrelevant results
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.35"))

# ============================================
# Hybrid Retrieval Configuration (NEW)
# ============================================
# Weight for dense retrieval (0-1), sparse gets (1 - DENSE_WEIGHT)
DENSE_WEIGHT = float(os.getenv("DENSE_WEIGHT", "0.7"))
# Minimum similarity score for dense retrieval
DENSE_SIMILARITY_THRESHOLD = float(os.getenv("DENSE_SIMILARITY_THRESHOLD", "0.35"))
# Minimum BM25 score for sparse retrieval
SPARSE_SIMILARITY_THRESHOLD = float(os.getenv("SPARSE_SIMILARITY_THRESHOLD", "0.1"))

# ============================================
# Ingestion Service Configuration (NEW)
# ============================================
# Directory to watch for new PDFs
PDF_WATCH_DIR = os.getenv("PDF_WATCH_DIR", str(PDF_DIR))
# Directory for processed PDFs
PROCESSED_PDF_DIR = os.getenv("PROCESSED_PDF_DIR", str(PROCESSED_DIR))
# Interval to check for new PDFs (in seconds)
INGESTION_CHECK_INTERVAL = int(os.getenv("INGESTION_CHECK_INTERVAL", "60"))
# Enable automatic ingestion on startup
AUTO_INGEST_ON_STARTUP = os.getenv("AUTO_INGEST_ON_STARTUP", "true").lower() == "true"

# Rate Limiting
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

# ============================================
# Security Configuration (NEW)
# ============================================
# JWT Authentication
JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "your-secret-key-change-this-in-production-use-openssl-rand-hex-32",
)
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# HTTPS Configuration
HTTPS_ONLY = os.getenv("HTTPS_ONLY", "false").lower() == "true"
TLS_MIN_VERSION = os.getenv("TLS_MIN_VERSION", "1.2")

# Checksum Verification
ENABLE_CHECKSUM_VERIFICATION = (
    os.getenv("ENABLE_CHECKSUM_VERIFICATION", "false").lower() == "true"
)
CHECKSUM_ALGORITHM = os.getenv("CHECKSUM_ALGORITHM", "sha256")  # md5 or sha256

# CORS Configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# Create logs directory
Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
