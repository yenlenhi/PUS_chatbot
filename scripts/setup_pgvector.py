"""
Setup pgvector extension for PostgreSQL database
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine, text
from config.settings import DATABASE_URL
from src.utils.logger import log


def setup_pgvector():
    """Setup pgvector extension in PostgreSQL"""
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Check if pgvector extension exists
            result = conn.execute(
                text("SELECT * FROM pg_available_extensions WHERE name = 'vector'")
            )
            extension_available = result.fetchone()
            
            if not extension_available:
                log.error("❌ pgvector extension is not available in PostgreSQL")
                log.error("Please install pgvector first:")
                log.error("  - For Docker: Use postgres image with pgvector")
                log.error("  - For local: Install from https://github.com/pgvector/pgvector")
                return False
            
            # Enable pgvector extension
            log.info("🔧 Enabling pgvector extension...")
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
            
            # Verify extension is installed
            result = conn.execute(
                text("SELECT * FROM pg_extension WHERE extname = 'vector'")
            )
            extension_installed = result.fetchone()
            
            if extension_installed:
                log.info("✅ pgvector extension is enabled")
                
                # Check vector type
                result = conn.execute(
                    text("SELECT typname FROM pg_type WHERE typname = 'vector'")
                )
                vector_type = result.fetchone()
                
                if vector_type:
                    log.info("✅ vector data type is available")
                else:
                    log.error("❌ vector data type is not available")
                    return False
                    
                return True
            else:
                log.error("❌ Failed to enable pgvector extension")
                return False
                
    except Exception as e:
        log.error(f"❌ Error setting up pgvector: {e}")
        return False


if __name__ == "__main__":
    log.info("=" * 60)
    log.info("Setting up pgvector extension")
    log.info("=" * 60)
    
    success = setup_pgvector()
    
    if success:
        log.info("=" * 60)
        log.info("✅ pgvector setup completed successfully")
        log.info("=" * 60)
    else:
        log.error("=" * 60)
        log.error("❌ pgvector setup failed")
        log.error("=" * 60)
        sys.exit(1)

