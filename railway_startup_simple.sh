#!/bin/bash

# Simplified Railway Startup Script for Debugging
set -e

echo "=========================================="
echo "🚂 Railway Startup (Simple Mode)"
echo "=========================================="

# Environment Check
echo ""
echo "[1/2] Environment Check..."
echo "DATABASE_URL: ${DATABASE_URL:0:30}..."
echo "PORT: ${PORT:-8000}"
echo "RAILWAY_VOLUME_MOUNT: ${RAILWAY_VOLUME_MOUNT:-/data}"

# Start Server Immediately
echo ""
echo "[2/2] Starting FastAPI server..."
echo "=========================================="

PORT="${PORT:-8000}"

exec python3 -m uvicorn main:app \
    --host 0.0.0.0 \
    --port "$PORT" \
    --log-level debug
