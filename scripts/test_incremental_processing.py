"""
Test script to verify incremental processing functionality
without actually processing files - just checks the logic
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.utils.logger import log
from src.services.database_service import DatabaseService

def test_get_processed_files():
    """Test getting processed files from database"""
    log.info("Testing get_processed_files()...")
    
    try:
        db_service = DatabaseService()
        processed_files = db_service.get_processed_files()
        
        log.info(f"Found {len(processed_files)} processed files:")
        for file in processed_files:
            log.info(f"  - {file}")
        
        return processed_files
        
    except Exception as e:
        log.error(f"Error testing get_processed_files: {e}")
        return []

def test_get_new_files():
    """Test identifying new files in not_process folder"""
    log.info("Testing new file detection...")
    
    try:
        # Get processed files
        db_service = DatabaseService()
        processed_files = set(db_service.get_processed_files())
        
        # Check not_process folder
        not_process_dir = Path("data/not_process")
        if not not_process_dir.exists():
            log.error(f"Directory {not_process_dir} does not exist")
            return []
        
        pdf_files = list(not_process_dir.glob("*.pdf"))
        new_files = []
        
        log.info(f"Files in not_process folder:")
        for pdf_file in pdf_files:
            is_new = pdf_file.name not in processed_files
            status = "NEW" if is_new else "ALREADY PROCESSED"
            log.info(f"  - {pdf_file.name} [{status}]")
            
            if is_new:
                new_files.append(pdf_file)
        
        log.info(f"Summary: {len(new_files)} new files found out of {len(pdf_files)} total")
        return new_files
        
    except Exception as e:
        log.error(f"Error testing new file detection: {e}")
        return []

def test_database_stats():
    """Test getting current database statistics"""
    log.info("Testing database statistics...")
    
    try:
        db_service = DatabaseService()
        
        # Get chunk count
        chunk_count = db_service.get_chunk_count()
        log.info(f"Current chunks in database: {chunk_count}")
        
        # Get all chunks (just count, don't load content)
        all_chunks = db_service.get_all_chunks()
        log.info(f"Chunks retrieved via get_all_chunks(): {len(all_chunks)}")
        
        # Verify consistency
        if chunk_count == len(all_chunks):
            log.info("✓ Database consistency check passed")
        else:
            log.warning(f"⚠ Database inconsistency: count={chunk_count}, retrieved={len(all_chunks)}")
        
        return chunk_count
        
    except Exception as e:
        log.error(f"Error testing database stats: {e}")
        return 0

def test_backup_functionality():
    """Test backup file creation logic"""
    log.info("Testing backup functionality...")
    
    try:
        from config.settings import PROCESSED_DIR
        chunks_file = PROCESSED_DIR / "heading_chunks.json"
        
        if chunks_file.exists():
            log.info(f"✓ Chunks file exists: {chunks_file}")
            
            # Check file size
            file_size = chunks_file.stat().st_size
            log.info(f"  File size: {file_size:,} bytes")
            
            # Test backup naming
            import time
            backup_name = f"heading_chunks_backup_{int(time.time())}.json"
            backup_path = PROCESSED_DIR / backup_name
            log.info(f"  Backup would be created as: {backup_path}")
            
        else:
            log.error(f"✗ Chunks file not found: {chunks_file}")
            
    except Exception as e:
        log.error(f"Error testing backup functionality: {e}")

def main():
    """Run all tests"""
    log.info("=" * 60)
    log.info("INCREMENTAL PROCESSING TEST")
    log.info("=" * 60)
    
    # Test 1: Get processed files
    log.info("\n" + "=" * 40)
    log.info("TEST 1: Get Processed Files")
    log.info("=" * 40)
    processed_files = test_get_processed_files()
    
    # Test 2: Identify new files
    log.info("\n" + "=" * 40)
    log.info("TEST 2: Identify New Files")
    log.info("=" * 40)
    new_files = test_get_new_files()
    
    # Test 3: Database statistics
    log.info("\n" + "=" * 40)
    log.info("TEST 3: Database Statistics")
    log.info("=" * 40)
    current_chunks = test_database_stats()
    
    # Test 4: Backup functionality
    log.info("\n" + "=" * 40)
    log.info("TEST 4: Backup Functionality")
    log.info("=" * 40)
    test_backup_functionality()
    
    # Summary
    log.info("\n" + "=" * 60)
    log.info("TEST SUMMARY")
    log.info("=" * 60)
    log.info(f"Current processed files: {len(processed_files)}")
    log.info(f"New files to process: {len(new_files)}")
    log.info(f"Current chunks in DB: {current_chunks}")
    
    if new_files:
        log.info("\n📋 READY FOR INCREMENTAL PROCESSING")
        log.info("New files that will be processed:")
        for file in new_files:
            log.info(f"  ✓ {file.name}")
        log.info(f"\nRun: python scripts/process_incremental_pdfs.py")
    else:
        log.info("\n✅ NO NEW FILES TO PROCESS")
        log.info("All files in not_process folder have already been processed.")
    
    log.info("=" * 60)

if __name__ == "__main__":
    main()
