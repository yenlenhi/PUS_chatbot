#!/usr/bin/env bash
set -euo pipefail

if [ -z "${LOCAL_DATABASE_URL:-}" ] || [ -z "${RAILWAY_DATABASE_URL:-}" ]; then
  echo "Please set LOCAL_DATABASE_URL and RAILWAY_DATABASE_URL environment variables"
  exit 1
fi

LOCAL_FILE="/work/local_tables.txt"
PROD_FILE="/work/prod_tables.txt"

echo "Querying local DB..."
psql "$LOCAL_DATABASE_URL" -Atc "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;" > "$LOCAL_FILE"

echo "Querying production DB..."
psql "$RAILWAY_DATABASE_URL" -Atc "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;" > "$PROD_FILE"

echo "--- LOCAL ---"
cat "$LOCAL_FILE"
echo "--- PROD ---"
cat "$PROD_FILE"

echo "--- IN LOCAL NOT IN PROD ---"
comm -23 "$LOCAL_FILE" "$PROD_FILE" || true

echo "--- IN PROD NOT IN LOCAL ---"
comm -13 "$LOCAL_FILE" "$PROD_FILE" || true
