Param()

# Usage from PowerShell (set env vars first):
# $env:LOCAL_DATABASE_URL = 'postgresql://user:pass@localhost:5432/local_db'
# $env:RAILWAY_DATABASE_URL = 'postgresql://user:pass@host:5432/pgvector_pus'
# ./scripts/migrate_to_railway.ps1

if (-not $env:LOCAL_DATABASE_URL -or -not $env:RAILWAY_DATABASE_URL) {
    Write-Error "Please set environment variables LOCAL_DATABASE_URL and RAILWAY_DATABASE_URL"
    exit 1
}

$local = $env:LOCAL_DATABASE_URL
$railway = $env:RAILWAY_DATABASE_URL
$tmp = Join-Path $PWD 'tmp_railway_dump.dump'

Write-Host "1) Creating custom-format dump from local DB..."
& pg_dump --format=custom --file=$tmp $local

Write-Host "2) Ensuring pgvector (vector) extension exists on Railway DB..."
& psql $railway -c "CREATE EXTENSION IF NOT EXISTS vector;"

Write-Host "3) Restoring dump into Railway DB (may take time)..."
& pg_restore --verbose --clean --no-owner --no-acl --dbname=$railway $tmp

Write-Host "4) Cleaning up..."
Remove-Item -Force $tmp

Write-Host "Migration complete. Verify data and indexes on Railway."
