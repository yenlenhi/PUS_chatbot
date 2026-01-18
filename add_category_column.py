import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add parent directory to path to allow imports if needed, though we're keeping this simple
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# Get Database URL
POSTGRES_USER = os.getenv("POSTGRES_USER", "uni_bot_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "uni_bot_password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "uni_bot_db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

RAILWAY_DATABASE_URL = os.getenv("RAILWAY_DATABASE_URL")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    RAILWAY_DATABASE_URL
    or f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}",
)

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print(f"Connecting to database...")

def migrate():
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='document_attachments' AND column_name='category'"
            ))
            if result.fetchone():
                print("Column 'category' already exists.")
            else:
                print("Adding 'category' column...")
                conn.execute(text("ALTER TABLE document_attachments ADD COLUMN category VARCHAR(50) DEFAULT 'Khác'"))
                conn.commit()
                print("Successfully added 'category' column.")
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate()
