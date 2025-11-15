"""
Script to fix incomplete PDF processing by removing chunks without embeddings
This allows files to be reprocessed properly
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.utils.logger import log
from src.services.database_service import DatabaseService


def main():
    """Main function to fix incomplete processing"""
    
    log.info("Starting incomplete processing fix...")
    
    try:
        # Initialize database service
        db_service = DatabaseService()
        
        # Get chunks without embeddings
        incomplete_chunks = db_service.get_chunks_without_embeddings()
        
        if not incomplete_chunks:
            log.info("No incomplete chunks found. All chunks have embeddings.")
            return
        
        # Group by source file
        files_with_issues = {}
        for chunk in incomplete_chunks:
            source_file = chunk['source_file']
            if source_file not in files_with_issues:
                files_with_issues[source_file] = []
            files_with_issues[source_file].append(chunk)
        
        log.info(f"Found {len(incomplete_chunks)} chunks without embeddings from {len(files_with_issues)} files:")
        
        for source_file, chunks in files_with_issues.items():
            log.info(f"  - {source_file}: {len(chunks)} chunks without embeddings")
        
        # Ask user for confirmation
        print("\nFiles with incomplete processing:")
        for i, source_file in enumerate(files_with_issues.keys(), 1):
            chunk_count = len(files_with_issues[source_file])
            print(f"{i}. {source_file} ({chunk_count} chunks without embeddings)")
        
        print("\nOptions:")
        print("1. Delete all incomplete chunks (recommended)")
        print("2. Show details of incomplete chunks")
        print("3. Exit without changes")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            # Delete incomplete chunks
            for source_file in files_with_issues.keys():
                log.info(f"Deleting incomplete chunks for: {source_file}")
                success = db_service.delete_chunks_by_file(source_file)
                if success:
                    log.info(f"Successfully deleted chunks for: {source_file}")
                else:
                    log.error(f"Failed to delete chunks for: {source_file}")
            
            log.info("Incomplete chunks cleanup completed!")
            log.info("You can now run process_incremental_pdfs.py to reprocess these files.")
            
        elif choice == "2":
            # Show details
            for source_file, chunks in files_with_issues.items():
                print(f"\n=== {source_file} ===")
                for chunk in chunks:
                    content_preview = chunk['content'][:100] + "..." if len(chunk['content']) > 100 else chunk['content']
                    print(f"  Chunk {chunk['chunk_index']}: {content_preview}")
            
        else:
            log.info("Exiting without changes.")
            
    except Exception as e:
        log.error(f"Error in incomplete processing fix: {e}")
        raise


if __name__ == "__main__":
    main()
