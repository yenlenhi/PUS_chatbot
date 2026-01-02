"""Export ALL tables from Docker PostgreSQL"""

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text, inspect
import numpy as np
from src.utils.logger import log

# Docker PostgreSQL URL
DOCKER_URL = "postgresql://uni_bot_user:uni_bot_password@localhost:5432/uni_bot_db"


def export_all_tables():
    """Export all tables from Docker PostgreSQL"""

    try:
        engine = create_engine(DOCKER_URL)
        inspector = inspect(engine)

        export_dir = Path("data/full_migration_export")
        export_dir.mkdir(parents=True, exist_ok=True)

        log.info("🔄 Connecting to Docker PostgreSQL...")

        # Get all table names
        table_names = inspector.get_table_names(schema="public")
        log.info(f"📊 Found {len(table_names)} tables: {', '.join(table_names)}")

        exported_tables = {}

        with engine.connect() as conn:
            for table_name in table_names:
                try:
                    log.info(f"\n📦 Exporting {table_name}...")

                    # Get columns for this table
                    columns = inspector.get_columns(table_name)
                    column_names = [col["name"] for col in columns]

                    # Special handling for embeddings with vector column
                    if table_name == "embeddings" and "embedding" in column_names:
                        result = conn.execute(
                            text(f"SELECT * FROM {table_name} ORDER BY id")
                        )
                        rows = []
                        for row in result:
                            row_dict = dict(row._mapping)
                            # Convert embedding
                            if row_dict.get("embedding"):
                                embedding_data = row_dict["embedding"]
                                if isinstance(embedding_data, str):
                                    import ast

                                    row_dict["embedding"] = ast.literal_eval(
                                        embedding_data
                                    )
                                elif isinstance(embedding_data, bytes):
                                    embedding_array = np.frombuffer(
                                        embedding_data, dtype=np.float32
                                    )
                                    row_dict["embedding"] = embedding_array.tolist()
                                else:
                                    row_dict["embedding"] = list(embedding_data)
                            if row_dict.get("created_at"):
                                row_dict["created_at"] = str(row_dict["created_at"])
                            rows.append(row_dict)
                    else:
                        # Regular table export
                        result = conn.execute(
                            text(f"SELECT * FROM {table_name} ORDER BY id")
                        )
                        rows = []
                        for row in result:
                            row_dict = dict(row._mapping)
                            # Convert datetime columns to string
                            for key, value in row_dict.items():
                                if hasattr(value, "isoformat"):  # datetime object
                                    row_dict[key] = str(value)
                            rows.append(row_dict)

                    # Save to JSON
                    output_file = export_dir / f"{table_name}.json"
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(rows, f, ensure_ascii=False, indent=2)

                    exported_tables[table_name] = len(rows)
                    log.info(f"  ✅ Exported {len(rows)} records")

                except Exception as e:
                    log.error(f"  ❌ Error exporting {table_name}: {e}")
                    exported_tables[table_name] = f"ERROR: {str(e)}"

        # Create summary
        summary = {
            "export_date": str(np.datetime64("now")),
            "source_database": "Docker PostgreSQL (localhost:5432)",
            "tables_exported": exported_tables,
            "total_tables": len(table_names),
        }

        with open(export_dir / "export_summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        log.info("\n" + "=" * 60)
        log.info("✅ Full export completed!")
        log.info(f"📂 Files saved to: {export_dir.absolute()}")
        log.info("=" * 60)

        for table, count in exported_tables.items():
            log.info(f"  {table}: {count}")

        log.info("=" * 60)

        return True

    except Exception as e:
        log.error(f"❌ Export failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    log.info("🚀 Starting FULL database export...")
    success = export_all_tables()
    sys.exit(0 if success else 1)
