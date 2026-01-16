# ============================================
# Multi-stage Docker build for University Chatbot
# Pre-downloads embedding models to avoid runtime download issues
# ============================================

# ============================================
# Stage 1: Model Download Stage
# ============================================
FROM python:3.11-slim as model-downloader

WORKDIR /models

# Install minimal dependencies for downloading models
RUN pip install --no-cache-dir \
    sentence-transformers==2.3.1 \
    torch==2.1.2 \
    transformers==4.36.2

# Pre-download the Vietnamese SBERT model
# This ensures the model is baked into the Docker image
RUN python -c "\
from sentence_transformers import SentenceTransformer; \
import os; \
os.environ['TRANSFORMERS_CACHE'] = '/models/cache'; \
os.environ['HF_HOME'] = '/models/cache'; \
print('📥 Downloading keepitreal/vietnamese-sbert...'); \
model = SentenceTransformer('keepitreal/vietnamese-sbert', cache_folder='/models/cache'); \
print('✅ Model downloaded successfully'); \
"

# Also download the fallback model
RUN python -c "\
from sentence_transformers import SentenceTransformer; \
import os; \
os.environ['TRANSFORMERS_CACHE'] = '/models/cache'; \
os.environ['HF_HOME'] = '/models/cache'; \
print('📥 Downloading fallback model: all-MiniLM-L6-v2...'); \
model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder='/models/cache'); \
print('✅ Fallback model downloaded successfully'); \
"

# ============================================
# Stage 2: Application Runtime Stage
# ============================================
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy pre-downloaded models from Stage 1
COPY --from=model-downloader /models/cache /root/.cache/huggingface

# Set environment variables for model cache
ENV TRANSFORMERS_CACHE=/root/.cache/huggingface
ENV HF_HOME=/root/.cache/huggingface
ENV SENTENCE_TRANSFORMERS_HOME=/root/.cache/huggingface
ENV HF_HUB_OFFLINE=1
ENV TRANSFORMERS_OFFLINE=1

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/pdfs data/processed data/embeddings logs

# Set permissions
RUN chmod -R 755 /app

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
