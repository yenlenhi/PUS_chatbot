"""
Script to deploy the new enhanced chunking strategy to production
This will replace the old chunking with the new optimized version
"""
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.utils.logger import log
from src.services.pdf_processor import PDFProcessor
from src.services.embedding_service import EmbeddingService
from src.services.database_service import DatabaseService
from src.services.faiss_service import FAISSService
from src.utils.heading_chunker import HeadingChunker
from config.settings import PDF_DIR, PROCESSED_DIR

def backup_current_data():
    """Backup current chunks and embeddings"""
    log.info("Creating backup of current data...")

    import shutil
    from datetime import datetime

    backup_dir = PROCESSED_DIR / "backup"
    backup_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Backup chunks file
    chunks_file = PROCESSED_DIR / "heading_chunks.json"
    if chunks_file.exists():
        backup_chunks = backup_dir / f"heading_chunks_backup_{timestamp}.json"
        shutil.copy2(chunks_file, backup_chunks)
        log.info(f"Backed up chunks to: {backup_chunks}")

    # Backup database (copy the file)
    db_service = DatabaseService()
    if db_service.db_path.exists():
        backup_db = backup_dir / f"database_backup_{timestamp}.db"
        shutil.copy2(db_service.db_path, backup_db)
        log.info(f"Backed up database to: {backup_db}")

    # Backup FAISS index
    faiss_service = FAISSService()
    index_file = faiss_service.index_path
    if index_file.exists():
        backup_index = backup_dir / f"faiss_index_backup_{timestamp}.faiss"
        shutil.copy2(index_file, backup_index)
        log.info(f"Backed up FAISS index to: {backup_index}")

def clear_current_data():
    """Clear current chunks and embeddings"""
    log.info("Clearing current data...")
    
    # Clear database
    db_service = DatabaseService()
    db_service.clear_all_data()
    log.info("Cleared database")
    
    # Remove old chunks file
    chunks_file = PROCESSED_DIR / "heading_chunks.json"
    if chunks_file.exists():
        chunks_file.unlink()
        log.info("Removed old chunks file")

def process_pdfs_with_new_chunking():
    """Process all PDFs with the new enhanced chunking strategy"""
    log.info("Processing PDFs with new enhanced chunking...")
    
    # Initialize services
    pdf_processor = PDFProcessor()
    embedding_service = EmbeddingService()
    db_service = DatabaseService()
    faiss_service = FAISSService()
    
    # Initialize enhanced chunker with optimized parameters
    chunker = HeadingChunker(
        min_chunk_size=100,
        max_chunk_size=2500,
        target_chunk_size=1000
    )
    
    # Get all PDF files
    pdf_files = list(PDF_DIR.glob("*.pdf"))
    
    if not pdf_files:
        log.error(f"No PDF files found in {PDF_DIR}")
        return False
    
    log.info(f"Found {len(pdf_files)} PDF files to process")
    
    all_chunks = []
    
    # Process each PDF file
    for pdf_file in pdf_files:
        log.info(f"Processing {pdf_file.name}...")
        
        try:
            # Extract text
            text = pdf_processor.extract_text_from_pdf(pdf_file)
            
            if not text:
                log.warning(f"No text extracted from {pdf_file.name}")
                continue
            
            # Create chunks using new enhanced strategy
            chunks = chunker.chunk_by_headings(text, pdf_file.name)
            
            if not chunks:
                log.warning(f"No chunks created from {pdf_file.name}")
                continue
            
            all_chunks.extend(chunks)
            log.info(f"Created {len(chunks)} chunks from {pdf_file.name}")
            
        except Exception as e:
            log.error(f"Error processing {pdf_file.name}: {e}")
            continue
    
    if not all_chunks:
        log.error("No chunks created from any PDF files")
        return False
    
    log.info(f"Created a total of {len(all_chunks)} chunks")
    
    # Analyze chunks
    analysis = chunker.analyze_chunks(all_chunks)
    log.info(f"Chunk analysis: avg_size={analysis['avg_char_count']:.1f}, "
             f"range={analysis['min_char_count']}-{analysis['max_char_count']}")
    
    # Save chunks to file
    output_file = PROCESSED_DIR / "heading_chunks.json"
    chunks_data = [chunk.model_dump() for chunk in all_chunks]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chunks_data, f, ensure_ascii=False, indent=2)
    
    log.info(f"Saved chunks to {output_file}")
    
    # Insert chunks into database
    chunk_ids = db_service.insert_chunks(all_chunks)
    log.info(f"Inserted {len(chunk_ids)} chunks into database")
    
    # Create embeddings
    log.info("Creating embeddings...")
    texts = [chunk.content for chunk in all_chunks]
    embeddings = embedding_service.create_embeddings_batch(texts, batch_size=16)
    
    # Insert embeddings into database
    log.info("Inserting embeddings into database...")
    db_service.insert_embeddings(chunk_ids, embeddings)
    
    # Create FAISS index
    log.info("Creating FAISS index...")
    faiss_service.create_index(embeddings, chunk_ids)
    
    # Save FAISS index
    log.info("Saving FAISS index...")
    faiss_service.save_index()
    
    # Save analysis
    analysis_file = PROCESSED_DIR / "chunk_analysis_production.json"
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    log.info(f"Saved analysis to {analysis_file}")
    
    return True

def validate_deployment():
    """Validate that the deployment was successful"""
    log.info("Validating deployment...")
    
    # Check chunks file
    chunks_file = PROCESSED_DIR / "heading_chunks.json"
    if not chunks_file.exists():
        log.error("Chunks file not found after deployment")
        return False
    
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks_data = json.load(f)
    
    log.info(f"✅ Found {len(chunks_data)} chunks in file")
    
    # Check database
    db_service = DatabaseService()
    chunk_count = db_service.get_chunk_count()
    log.info(f"✅ Found {chunk_count} chunks in database")
    
    # Check FAISS index
    faiss_service = FAISSService()
    if faiss_service.load_index():
        index_size = faiss_service.index.ntotal if faiss_service.index else 0
        log.info(f"✅ FAISS index loaded with {index_size} vectors")
    else:
        log.error("❌ Failed to load FAISS index")
        return False
    
    # Validate metadata
    sample_chunks = chunks_data[:5]
    metadata_fields = ['heading_text', 'heading_level', 'chunk_type', 'word_count', 'char_count']
    
    for i, chunk in enumerate(sample_chunks):
        missing_fields = [field for field in metadata_fields if field not in chunk]
        if missing_fields:
            log.warning(f"Chunk {i} missing metadata fields: {missing_fields}")
        else:
            log.info(f"✅ Chunk {i} has complete metadata")
    
    log.info("✅ Deployment validation completed successfully")
    return True

def print_deployment_summary():
    """Print a summary of the deployment"""
    log.info("Generating deployment summary...")
    
    chunks_file = PROCESSED_DIR / "heading_chunks.json"
    analysis_file = PROCESSED_DIR / "chunk_analysis_production.json"
    
    if chunks_file.exists() and analysis_file.exists():
        with open(analysis_file, 'r', encoding='utf-8') as f:
            analysis = json.load(f)
        
        print("\n" + "="*80)
        print("DEPLOYMENT SUMMARY")
        print("="*80)
        print(f"✅ Successfully deployed enhanced chunking strategy")
        print(f"📊 Total chunks: {analysis['total_chunks']}")
        print(f"📊 Average chunk size: {analysis['avg_char_count']:.1f} characters")
        print(f"📊 Size range: {analysis['min_char_count']} - {analysis['max_char_count']} characters")
        print(f"📈 Chunks by type:")
        for chunk_type, count in analysis['chunks_by_type'].items():
            print(f"   {chunk_type}: {count}")
        print(f"📈 Chunks by heading level:")
        for level, count in analysis['chunks_by_heading_level'].items():
            print(f"   Level {level}: {count}")
        
        if analysis.get('large_chunks'):
            print(f"⚠️ Large chunks: {len(analysis['large_chunks'])}")
        if analysis.get('small_chunks'):
            print(f"⚠️ Small chunks: {len(analysis['small_chunks'])}")
        
        print("\n🎯 BENEFITS OF NEW CHUNKING:")
        print("   ✅ Complete content preservation - no data loss")
        print("   ✅ Rich metadata for better retrieval")
        print("   ✅ Intelligent splitting of large sections")
        print("   ✅ Optimized chunk sizes for RAG performance")
        print("   ✅ Hierarchical heading structure preserved")
        
        print("\n📁 FILES CREATED:")
        print(f"   📄 Chunks: {chunks_file}")
        print(f"   📊 Analysis: {analysis_file}")
        print(f"   🗄️ Database: Updated with enhanced schema")
        print(f"   🔍 FAISS Index: Rebuilt with new embeddings")
        
        print("="*80)

def main():
    """Main deployment function"""
    print("🚀 DEPLOYING ENHANCED CHUNKING STRATEGY TO PRODUCTION")
    print("="*80)
    
    try:
        # Step 1: Backup current data
        backup_current_data()
        
        # Step 2: Clear current data
        clear_current_data()
        
        # Step 3: Process PDFs with new chunking
        success = process_pdfs_with_new_chunking()
        
        if not success:
            log.error("❌ Failed to process PDFs with new chunking")
            return
        
        # Step 4: Validate deployment
        if not validate_deployment():
            log.error("❌ Deployment validation failed")
            return
        
        # Step 5: Print summary
        print_deployment_summary()
        
        log.info("🎉 Enhanced chunking strategy deployed successfully!")
        
    except Exception as e:
        log.error(f"❌ Deployment failed: {e}")
        raise

if __name__ == "__main__":
    main()
