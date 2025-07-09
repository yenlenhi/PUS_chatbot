"""
Script to completely reset database and rebuild from scratch
"""
import os
import sys
import shutil
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.utils.logger import log
from src.services.database_service import DatabaseService
from src.services.faiss_service import FAISSService
from config.settings import DATABASE_PATH, FAISS_INDEX_PATH, PROCESSED_DIR

def backup_before_reset():
    """Create backup before resetting"""
    try:
        from datetime import datetime
        
        backup_dir = PROCESSED_DIR / "backup"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Backup database
        if os.path.exists(DATABASE_PATH):
            backup_db = backup_dir / f"database_backup_{timestamp}.db"
            shutil.copy2(DATABASE_PATH, backup_db)
            log.info(f"✅ Database backed up to: {backup_db}")
        
        # Backup chunks file
        chunks_file = PROCESSED_DIR / "heading_chunks.json"
        if chunks_file.exists():
            backup_chunks = backup_dir / f"chunks_backup_{timestamp}.json"
            shutil.copy2(chunks_file, backup_chunks)
            log.info(f"✅ Chunks backed up to: {backup_chunks}")
        
        # Backup FAISS index
        if os.path.exists(FAISS_INDEX_PATH):
            backup_faiss = backup_dir / f"faiss_backup_{timestamp}"
            shutil.copytree(FAISS_INDEX_PATH, backup_faiss)
            log.info(f"✅ FAISS index backed up to: {backup_faiss}")
            
    except Exception as e:
        log.warning(f"Backup failed: {e}")

def reset_database():
    """Reset SQLite database"""
    try:
        if os.path.exists(DATABASE_PATH):
            os.remove(DATABASE_PATH)
            log.info(f"✅ Removed database file: {DATABASE_PATH}")
        else:
            log.info("No database file to remove")
            
        # Initialize new database with updated schema
        db_service = DatabaseService()
        log.info("✅ Initialized new database with enhanced schema")
        
    except Exception as e:
        log.error(f"Error resetting database: {e}")
        raise

def reset_faiss_index():
    """Reset FAISS index"""
    try:
        if os.path.exists(FAISS_INDEX_PATH):
            shutil.rmtree(FAISS_INDEX_PATH)
            log.info(f"✅ Removed FAISS index directory: {FAISS_INDEX_PATH}")
        else:
            log.info("No FAISS index to remove")
            
    except Exception as e:
        log.error(f"Error resetting FAISS index: {e}")
        raise

def reset_processed_files():
    """Reset processed files"""
    try:
        chunks_file = PROCESSED_DIR / "heading_chunks.json"
        if chunks_file.exists():
            chunks_file.unlink()
            log.info(f"✅ Removed chunks file: {chunks_file}")
        
        # Remove analysis files
        analysis_files = [
            PROCESSED_DIR / "chunk_analysis.json",
            PROCESSED_DIR / "chunk_analysis_production.json"
        ]
        
        for file in analysis_files:
            if file.exists():
                file.unlink()
                log.info(f"✅ Removed analysis file: {file}")
                
    except Exception as e:
        log.error(f"Error resetting processed files: {e}")
        raise

def rebuild_from_pdfs():
    """Rebuild everything from PDF files"""
    try:
        log.info("🔄 Rebuilding from PDF files...")
        
        # Import here to avoid circular imports
        from src.services.pdf_processor import PDFProcessor
        from src.services.embedding_service import EmbeddingService
        from src.utils.heading_chunker import HeadingChunker
        from config.settings import PDF_DIR
        
        # Initialize services
        pdf_processor = PDFProcessor()
        embedding_service = EmbeddingService()
        db_service = DatabaseService()
        faiss_service = FAISSService()
        
        # Initialize enhanced chunker
        chunker = HeadingChunker(
            min_chunk_size=100,
            max_chunk_size=2500,
            target_chunk_size=1000
        )
        
        # Get PDF files
        pdf_files = list(PDF_DIR.glob("*.pdf"))
        
        if not pdf_files:
            log.warning(f"No PDF files found in {PDF_DIR}")
            return False
        
        log.info(f"Found {len(pdf_files)} PDF files to process")
        
        all_chunks = []
        
        # Process each PDF
        for pdf_file in pdf_files:
            log.info(f"Processing {pdf_file.name}...")
            
            # Extract text
            text = pdf_processor.extract_text_from_pdf(pdf_file)
            if not text:
                log.warning(f"No text extracted from {pdf_file.name}")
                continue
            
            # Create chunks
            chunks = chunker.chunk_by_headings(text, pdf_file.name)
            if chunks:
                all_chunks.extend(chunks)
                log.info(f"Created {len(chunks)} chunks from {pdf_file.name}")
        
        if not all_chunks:
            log.error("No chunks created")
            return False
        
        log.info(f"Created total of {len(all_chunks)} chunks")
        
        # Save chunks
        import json
        chunks_file = PROCESSED_DIR / "heading_chunks.json"
        chunks_data = [chunk.model_dump() for chunk in all_chunks]
        
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(chunks_data, f, ensure_ascii=False, indent=2)
        
        log.info(f"✅ Saved chunks to {chunks_file}")
        
        # Insert into database
        chunk_ids = db_service.insert_chunks(all_chunks)
        log.info(f"✅ Inserted {len(chunk_ids)} chunks into database")
        
        # Create embeddings
        log.info("Creating embeddings...")
        texts = [chunk.content for chunk in all_chunks]
        embeddings = embedding_service.create_embeddings_batch(texts, batch_size=16)
        
        # Insert embeddings
        db_service.insert_embeddings(chunk_ids, embeddings)
        log.info("✅ Inserted embeddings into database")
        
        # Create FAISS index
        log.info("Creating FAISS index...")
        faiss_service.create_index(embeddings, chunk_ids)
        faiss_service.save_index()
        log.info("✅ Created and saved FAISS index")
        
        # Analyze chunks
        analysis = chunker.analyze_chunks(all_chunks)
        analysis_file = PROCESSED_DIR / "chunk_analysis_production.json"
        
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        
        log.info(f"✅ Saved analysis to {analysis_file}")
        
        return True
        
    except Exception as e:
        log.error(f"Error rebuilding from PDFs: {e}")
        raise

def main():
    """Main reset and rebuild function"""
    print("🔄 RESET AND REBUILD DATABASE FROM SCRATCH")
    print("="*60)
    
    try:
        # Step 1: Backup current data
        log.info("Step 1: Creating backup...")
        backup_before_reset()
        
        # Step 2: Reset database
        log.info("Step 2: Resetting database...")
        reset_database()
        
        # Step 3: Reset FAISS index
        log.info("Step 3: Resetting FAISS index...")
        reset_faiss_index()
        
        # Step 4: Reset processed files
        log.info("Step 4: Resetting processed files...")
        reset_processed_files()
        
        # Step 5: Rebuild from PDFs
        log.info("Step 5: Rebuilding from PDFs...")
        success = rebuild_from_pdfs()
        
        if success:
            print("\n🎉 RESET AND REBUILD COMPLETED SUCCESSFULLY!")
            print("✅ Database reset and recreated with enhanced schema")
            print("✅ All PDFs reprocessed with new chunking strategy")
            print("✅ Embeddings and FAISS index rebuilt")
            print("✅ Backup created before reset")
        else:
            log.error("❌ Rebuild failed")
            
    except Exception as e:
        log.error(f"❌ Reset and rebuild failed: {e}")
        raise

if __name__ == "__main__":
    main()
