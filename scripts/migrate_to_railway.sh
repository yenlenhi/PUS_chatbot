#!/usr/bin/env bash
set -euo pipefail

# Usage:
# LOCAL_DATABASE_URL=postgresql://user:pass@localhost:5432/local_db \
# RAILWAY_DATABASE_URL=postgresql://user:pass@host:5432/pgvector_pus \
# ./scripts/migrate_to_railway.sh

LOCAL_DATABASE_URL="${LOCAL_DATABASE_URL:-}"
RAILWAY_DATABASE_URL="${RAILWAY_DATABASE_URL:-}"

if [ -z "$LOCAL_DATABASE_URL" ] || [ -z "$RAILWAY_DATABASE_URL" ]; then
  echo "ERROR: Please set LOCAL_DATABASE_URL and RAILWAY_DATABASE_URL environment variables."
  echo "Example: LOCAL_DATABASE_URL=postgresql://user:pass@localhost:5432/uni_bot_db"
  exit 1
fi

TMP_DUMP="./tmp_railway_dump.dump"

echo "1) Creating custom-format dump from local DB..."
pg_dump --format=custom --file="$TMP_DUMP" "$LOCAL_DATABASE_URL"

echo "2) Ensuring pgvector (vector) extension exists on Railway DB..."
psql "$RAILWAY_DATABASE_URL" -c "CREATE EXTENSION IF NOT EXISTS vector;"

echo "3) Restoring dump into Railway DB (may take time)..."
pg_restore --verbose --clean --no-owner --no-acl --dbname="$RAILWAY_DATABASE_URL" "$TMP_DUMP"

echo "4) Done. Clean up temporary dump file: $TMP_DUMP"
rm -f "$TMP_DUMP"

echo "Migration complete. Verify data and indexes on Railway."
