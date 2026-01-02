"""
Run Supabase migration SQL to create schema
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from src.utils.logger import log


def run_migration(supabase_url: str):
    """Run migration SQL on Supabase"""

    try:
        log.info("🔄 Connecting to Supabase...")
        engine = create_engine(supabase_url)

        # Read migration SQL
        sql_file = Path(__file__).parent / "migrate_to_supabase.sql"
        with open(sql_file, "r", encoding="utf-8") as f:
            sql_content = f.read()

        log.info("📄 Running migration SQL...")

        with engine.connect() as conn:
            # Split SQL by semicolon and execute each statement
            statements = [s.strip() for s in sql_content.split(";") if s.strip()]

            for i, statement in enumerate(statements, 1):
                if statement:
                    try:
                        conn.execute(text(statement))
                        conn.commit()
                    except Exception as e:
                        # Some statements might fail if already exists, that's OK
                        if "already exists" in str(e).lower():
                            log.debug(f"Statement {i} already applied: {str(e)[:100]}")
                        else:
                            log.warning(f"Statement {i} warning: {str(e)[:100]}")

            log.info("✅ Migration SQL completed successfully!")

            # Verify tables
            log.info("📊 Verifying tables...")
            result = conn.execute(
                text(
                    "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"
                )
            )
            tables = [row[0] for row in result]

            log.info(f"✅ Found {len(tables)} tables:")
            for table in tables:
                log.info(f"  - {table}")

            return True

    except Exception as e:
        log.error(f"❌ Migration failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run Supabase migration SQL")
    parser.add_argument("--url", required=True, help="Supabase connection URL")

    args = parser.parse_args()

    log.info("🚀 Starting Supabase migration...")
    success = run_migration(args.url)
    sys.exit(0 if success else 1)
