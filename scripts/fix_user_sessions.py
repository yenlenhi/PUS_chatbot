"""Fix missing columns in database tables"""

import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()


def fix_database():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()

    # Check user_sessions table columns
    cur.execute(
        "SELECT column_name FROM information_schema.columns WHERE table_name = 'user_sessions'"
    )
    columns = [row[0] for row in cur.fetchall()]
    print(f"user_sessions columns: {columns}")

    # Add created_at if missing
    if "created_at" not in columns:
        cur.execute(
            "ALTER TABLE user_sessions ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        )
        print("✅ Added created_at column to user_sessions")
    else:
        print("✅ created_at already exists in user_sessions")

    conn.commit()
    cur.close()
    conn.close()
    print("Done!")


if __name__ == "__main__":
    fix_database()
