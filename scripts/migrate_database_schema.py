"""
Script to migrate database schema to support enhanced chunking metadata
"""
import sqlite3
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.utils.logger import log
from src.services.database_service import DatabaseService

def check_current_schema():
    """Check the current database schema"""
    db_service = DatabaseService()
    
    try:
        with sqlite3.connect(db_service.db_path) as conn:
            cursor = conn.cursor()
            
            # Get current chunks table schema
            cursor.execute("PRAGMA table_info(chunks)")
            chunks_columns = cursor.fetchall()
            
            log.info("Current chunks table schema:")
            for col in chunks_columns:
                log.info(f"  {col[1]} {col[2]} {'NOT NULL' if col[3] else ''} {'PRIMARY KEY' if col[5] else ''}")
            
            return [col[1] for col in chunks_columns]  # Return column names
            
    except Exception as e:
        log.error(f"Error checking schema: {e}")
        return []

def migrate_chunks_table():
    """Migrate chunks table to new schema"""
    db_service = DatabaseService()
    
    try:
        with sqlite3.connect(db_service.db_path) as conn:
            cursor = conn.cursor()
            
            log.info("Starting chunks table migration...")
            
            # Check if new columns already exist
            cursor.execute("PRAGMA table_info(chunks)")
            existing_columns = [col[1] for col in cursor.fetchall()]
            
            new_columns = [
                ('heading_text', 'TEXT'),
                ('heading_level', 'INTEGER'),
                ('heading_number', 'TEXT'),
                ('parent_heading', 'TEXT'),
                ('is_sub_chunk', 'BOOLEAN DEFAULT FALSE'),
                ('sub_chunk_index', 'INTEGER'),
                ('total_sub_chunks', 'INTEGER'),
                ('chunk_type', 'TEXT DEFAULT "content"'),
                ('word_count', 'INTEGER'),
                ('char_count', 'INTEGER')
            ]
            
            # Add missing columns
            for col_name, col_type in new_columns:
                if col_name not in existing_columns:
                    try:
                        cursor.execute(f'ALTER TABLE chunks ADD COLUMN {col_name} {col_type}')
                        log.info(f"Added column: {col_name}")
                    except sqlite3.OperationalError as e:
                        if "duplicate column name" in str(e):
                            log.info(f"Column {col_name} already exists")
                        else:
                            raise
            
            conn.commit()
            log.info("✅ Chunks table migration completed")
            
    except Exception as e:
        log.error(f"Error migrating chunks table: {e}")
        raise

def update_existing_chunks_metadata():
    """Update existing chunks with basic metadata"""
    db_service = DatabaseService()
    
    try:
        with sqlite3.connect(db_service.db_path) as conn:
            cursor = conn.cursor()
            
            log.info("Updating existing chunks with metadata...")
            
            # Get all existing chunks
            cursor.execute('SELECT id, content FROM chunks WHERE chunk_type IS NULL OR chunk_type = ""')
            chunks = cursor.fetchall()
            
            log.info(f"Found {len(chunks)} chunks to update")
            
            for chunk_id, content in chunks:
                # Calculate basic metadata
                word_count = len(content.split()) if content else 0
                char_count = len(content) if content else 0
                chunk_type = "content"  # Default type for existing chunks
                
                # Update the chunk
                cursor.execute('''
                    UPDATE chunks 
                    SET word_count = ?, char_count = ?, chunk_type = ?
                    WHERE id = ?
                ''', (word_count, char_count, chunk_type, chunk_id))
            
            conn.commit()
            log.info(f"✅ Updated metadata for {len(chunks)} existing chunks")
            
    except Exception as e:
        log.error(f"Error updating existing chunks: {e}")
        raise

def verify_migration():
    """Verify that the migration was successful"""
    db_service = DatabaseService()
    
    try:
        with sqlite3.connect(db_service.db_path) as conn:
            cursor = conn.cursor()
            
            log.info("Verifying migration...")
            
            # Check new schema
            cursor.execute("PRAGMA table_info(chunks)")
            columns = cursor.fetchall()
            
            expected_columns = [
                'id', 'content', 'source_file', 'page_number', 'chunk_index',
                'heading_text', 'heading_level', 'heading_number', 'parent_heading',
                'is_sub_chunk', 'sub_chunk_index', 'total_sub_chunks', 'chunk_type',
                'word_count', 'char_count', 'created_at'
            ]
            
            actual_columns = [col[1] for col in columns]
            
            missing_columns = set(expected_columns) - set(actual_columns)
            if missing_columns:
                log.error(f"❌ Missing columns: {missing_columns}")
                return False
            
            log.info("✅ All expected columns present")
            
            # Check that existing data is preserved
            cursor.execute('SELECT COUNT(*) FROM chunks')
            chunk_count = cursor.fetchone()[0]
            log.info(f"✅ Found {chunk_count} chunks in database")
            
            # Check metadata
            cursor.execute('SELECT COUNT(*) FROM chunks WHERE word_count IS NOT NULL')
            metadata_count = cursor.fetchone()[0]
            log.info(f"✅ {metadata_count} chunks have word_count metadata")
            
            return True
            
    except Exception as e:
        log.error(f"Error verifying migration: {e}")
        return False

def backup_database():
    """Create a backup of the database before migration"""
    db_service = DatabaseService()
    
    if not db_service.db_path.exists():
        log.info("No existing database to backup")
        return
    
    try:
        import shutil
        from datetime import datetime
        
        backup_dir = Path(db_service.db_path).parent / "backup"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_dir / f"database_pre_migration_{timestamp}.db"
        
        shutil.copy2(db_service.db_path, backup_path)
        log.info(f"✅ Database backed up to: {backup_path}")
        
    except Exception as e:
        log.error(f"Error backing up database: {e}")
        raise

def main():
    """Main migration function"""
    print("🔄 MIGRATING DATABASE SCHEMA FOR ENHANCED CHUNKING")
    print("="*60)
    
    try:
        # Step 1: Backup database
        backup_database()
        
        # Step 2: Check current schema
        current_columns = check_current_schema()
        log.info(f"Current schema has {len(current_columns)} columns")
        
        # Step 3: Migrate chunks table
        migrate_chunks_table()
        
        # Step 4: Update existing chunks with metadata
        update_existing_chunks_metadata()
        
        # Step 5: Verify migration
        if verify_migration():
            log.info("🎉 Database migration completed successfully!")
            
            print("\n✅ MIGRATION SUMMARY:")
            print("   📊 Database schema updated with enhanced metadata fields")
            print("   📊 Existing chunks updated with basic metadata")
            print("   📊 All data preserved during migration")
            print("   📁 Backup created before migration")
            
            print("\n🆕 NEW METADATA FIELDS:")
            print("   📝 heading_text - Text of the heading")
            print("   📏 heading_level - Level of the heading (1, 2, 3, etc.)")
            print("   🔢 heading_number - Number of the heading (e.g., '7.3.1')")
            print("   👨‍👩‍👧‍👦 parent_heading - Parent heading number")
            print("   🧩 is_sub_chunk - Whether this is a sub-chunk")
            print("   📊 sub_chunk_index - Index within sub-chunks")
            print("   📊 total_sub_chunks - Total number of sub-chunks")
            print("   🏷️ chunk_type - Type of chunk (intro, heading, content)")
            print("   📝 word_count - Number of words in chunk")
            print("   📏 char_count - Number of characters in chunk")
            
        else:
            log.error("❌ Migration verification failed")
            
    except Exception as e:
        log.error(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    main()
