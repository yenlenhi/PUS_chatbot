**Railway Migration**

This document describes how to migrate your local Postgres database (including pgvector data) to the Railway database named `pgvector_pus`.

**Prerequisites**: `pg_dump`, `pg_restore`, and `psql` must be installed locally and available on PATH. You must have Railway DB connection string (set as `RAILWAY_DATABASE_URL`).

**Important**: Ensure you have backups and that the Railway DB can accept your import. Restoring will modify the target DB.

Steps (recommended):

1) Export local DB (custom format):

  - Bash:

    ```bash
    LOCAL_DATABASE_URL=postgresql://user:pass@localhost:5432/uni_bot_db \
    RAILWAY_DATABASE_URL=postgresql://user:pass@host:5432/pgvector_pus \
    ./scripts/migrate_to_railway.sh
    ```

  - PowerShell:

    ```powershell
    $env:LOCAL_DATABASE_URL = 'postgresql://user:pass@localhost:5432/uni_bot_db'
    $env:RAILWAY_DATABASE_URL = 'postgresql://user:pass@host:5432/pgvector_pus'
    ./scripts/migrate_to_railway.ps1
    ```

What the scripts do:

- Create a custom-format `pg_dump` of the local DB.
- Run `CREATE EXTENSION IF NOT EXISTS vector` on the Railway DB to ensure `pgvector` is available.
- Use `pg_restore` to restore the dump into the Railway DB with `--clean --no-owner --no-acl` to avoid ownership/ACL issues.

Post-migration checks:

- Run `psql "$RAILWAY_DATABASE_URL" -c "SELECT COUNT(*) FROM <important_table>;"` for a few tables.
- Run `python test_postgres_connection.py` after setting `DATABASE_URL` to the Railway URL to verify pgvector and tables.

Troubleshooting:

- If `CREATE EXTENSION vector` fails, check whether your Railway plan supports extensions and contact Railway support or enable the extension via the Railway DB UI.
- For permission errors, consider creating the same roles or adjust restore flags.

Rollback: If import produced unwanted state, restore from Railway's backup (if available) or drop/clean public schema and re-import a previous dump.
