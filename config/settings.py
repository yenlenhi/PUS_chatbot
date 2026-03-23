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

# OCR configuration for uploaded/scanned PDFs
PDF_OCR_LANGUAGES = os.getenv("PDF_OCR_LANGUAGES", "vie+eng")
PDF_OCR_DPI = int(os.getenv("PDF_OCR_DPI", "200"))
PDF_OCR_MIN_TEXT_CHARS = int(os.getenv("PDF_OCR_MIN_TEXT_CHARS", "20"))
PDF_TEXT_EXTRACTION_MODE = os.getenv("PDF_TEXT_EXTRACTION_MODE", "gemini_only").lower()
PDF_GEMINI_RENDER_SCALE = float(os.getenv("PDF_GEMINI_RENDER_SCALE", "3.0"))

# Ensure directories exist
PDF_DIR.mkdir(parents=True, exist_ok=True)
NEW_PDF_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)


# LLM Provider Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "")  # "ollama" or "gemini"

# Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = os.getenv(
    "GEMINI_API_URL",
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent",
)
GEMINI_MAX_OUTPUT_TOKENS = int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "8192"))
GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
# Enable/disable Gemini question normalization (disabled: saves 2-3s, always hits MAX_TOKENS)
ENABLE_GEMINI_NORMALIZATION = (
    os.getenv("ENABLE_GEMINI_NORMALIZATION", "false").lower() == "true"
)

# Enable/disable Google Search Grounding for real-time information
# When enabled, queries about current affairs (leaders, news, events) will
# automatically use Google Search to get up-to-date information
ENABLE_GOOGLE_SEARCH_GROUNDING = (
    os.getenv("ENABLE_GOOGLE_SEARCH_GROUNDING", "true").lower() == "true"
)

# Product policy: chatbot answers all university-related questions (not just admission)
# Set ADMISSION_ONLY_MODE=true to restrict to admission topics only
ADMISSION_ONLY_MODE = os.getenv("ADMISSION_ONLY_MODE", "false").lower() == "true"

# ============================================
# ACCURACY MODE CONFIGURATION
# ============================================
# STRICT_MODE: Only answer from official documents, fallback when confidence low
STRICT_MODE = os.getenv("STRICT_MODE", "true").lower() == "true"

# Minimum confidence threshold to provide an answer (0.0 - 1.0)
# If confidence < threshold AND query is an ambiguous score query, bot returns clarification
# For non-score queries the bot still attempts to answer using available context
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.45"))

# Require source citation in answers
REQUIRE_SOURCE_CITATION = os.getenv("REQUIRE_SOURCE_CITATION", "true").lower() == "true"

# Performance instrumentation for stage-by-stage latency analysis
ENABLE_STAGE_TIMINGS = os.getenv("ENABLE_STAGE_TIMINGS", "true").lower() == "true"

# Prewarm retrieval + reranker models on startup so the first demo question
# does not pay the full lazy-loading cost.
PREWARM_RAG_ON_STARTUP = os.getenv("PREWARM_RAG_ON_STARTUP", "true").lower() == "true"

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

# ============================================
# Rate Limiting Configuration
# ============================================
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
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

# Embedding Dimension Configuration
# Auto-detect based on model, or set manually via EMBEDDING_DIMENSION env var
# Common dimensions: 384 (MiniLM, vietnamese-sbert), 768 (halong_embedding, vietnamese-embedding-v1)
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "384"))

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
HEADING_CHUNK_MIN_SIZE = int(os.getenv("HEADING_CHUNK_MIN_SIZE", "800"))
HEADING_CHUNK_TARGET_SIZE = int(os.getenv("HEADING_CHUNK_TARGET_SIZE", "2600"))
HEADING_CHUNK_MAX_SIZE = int(os.getenv("HEADING_CHUNK_MAX_SIZE", "5500"))
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "12"))
# Set a stricter threshold to filter out irrelevant results
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.30"))

# ============================================
# Hybrid Retrieval Configuration (NEW)
# ============================================
# Weight for dense retrieval (0-1), sparse gets (1 - DENSE_WEIGHT)
DENSE_WEIGHT = float(os.getenv("DENSE_WEIGHT", "0.7"))
# Minimum similarity score for dense retrieval (lower = more recall, fewer relevant docs filtered out)
DENSE_SIMILARITY_THRESHOLD = float(os.getenv("DENSE_SIMILARITY_THRESHOLD", "0.28"))
# Minimum BM25 score for sparse retrieval
SPARSE_SIMILARITY_THRESHOLD = float(os.getenv("SPARSE_SIMILARITY_THRESHOLD", "0.15"))
RETRIEVAL_INITIAL_K_MULTIPLIER = int(os.getenv("RETRIEVAL_INITIAL_K_MULTIPLIER", "3"))
RETRIEVAL_INITIAL_K_CAP = int(os.getenv("RETRIEVAL_INITIAL_K_CAP", "50"))
RERANK_MAX_CANDIDATES = int(os.getenv("RERANK_MAX_CANDIDATES", "15"))
ENABLE_CONTEXT_EXPANSION = (
    os.getenv("ENABLE_CONTEXT_EXPANSION", "true").lower() == "true"
)
CONTEXT_EXPANSION_MAX_NEIGHBORS = int(os.getenv("CONTEXT_EXPANSION_MAX_NEIGHBORS", "2"))
CONTEXT_EXPANSION_SKIP_TOP_SCORE = float(
    os.getenv("CONTEXT_EXPANSION_SKIP_TOP_SCORE", "0.85")
)
CONTEXT_EXPANSION_SKIP_SECONDARY_SCORE = float(
    os.getenv("CONTEXT_EXPANSION_SKIP_SECONDARY_SCORE", "0.75")
)

# ============================================
# Attachment Retrieval Configuration (NEW)
# ============================================
# Maximum number of attachments to include in context
MAX_ATTACHMENTS_IN_CONTEXT = int(os.getenv("MAX_ATTACHMENTS_IN_CONTEXT", "3"))
# Minimum relevance score threshold for attachments (0.0-1.0)
MIN_ATTACHMENT_SCORE_THRESHOLD = float(
    os.getenv("MIN_ATTACHMENT_SCORE_THRESHOLD", "0.75")
)

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

# ============================================
# Supabase Storage Configuration (NEW)
# ============================================
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv(
    "SUPABASE_SERVICE_KEY", ""
)  # Service role key for server-side uploads
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_STORAGE_BUCKET = os.getenv("SUPABASE_STORAGE_BUCKET", "documents")

# Create logs directory
Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
