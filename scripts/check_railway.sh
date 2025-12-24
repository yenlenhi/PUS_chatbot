#!/usr/bin/env bash
set -euo pipefail

if [ -z "${RAILWAY_DATABASE_URL:-}" ]; then
  echo "Please set RAILWAY_DATABASE_URL environment variable"
  exit 1
fi

echo "Checking pgvector extension..."
psql "$RAILWAY_DATABASE_URL" -c "SELECT extname FROM pg_extension WHERE extname='vector';"

echo "Counting rows in chunks..."
psql "$RAILWAY_DATABASE_URL" -c "SELECT COUNT(*) FROM chunks;"

echo "Counting rows in embeddings..."
psql "$RAILWAY_DATABASE_URL" -c "SELECT COUNT(*) FROM embeddings;"
