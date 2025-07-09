"""
Script to process PDFs using heading-based chunking
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
from config.settings import PDF_DIR, PROCESSED_DIR

def main():
    """Process PDFs and create heading-based chunks"""
    log.info("Starting PDF processing with heading-based chunking...")
    
    try:
        # Initialize services
        pdf_processor = PDFProcessor()
        embedding_service = EmbeddingService()
        db_service = DatabaseService()
        faiss_service = FAISSService()
        
        # Get all PDF files
        pdf_files = list(PDF_DIR.glob("*.pdf"))
        
        if not pdf_files:
            log.error(f"No PDF files found in {PDF_DIR}")
            return
        
        log.info(f"Found {len(pdf_files)} PDF files")
        
        # Process each PDF file
        all_chunks = []
        
        for pdf_file in pdf_files:
            log.info(f"Processing {pdf_file.name}...")
            
            # Process PDF with heading-based chunking
            chunks = pdf_processor.process_pdf_with_headings(pdf_file)
            
            if not chunks:
                log.warning(f"No chunks created from {pdf_file.name}")
                continue
            
            all_chunks.extend(chunks)
        
        if not all_chunks:
            log.error("No chunks created from any PDF files")
            return
        
        log.info(f"Created a total of {len(all_chunks)} chunks")
        
        # Save chunks to file
        output_file = PROCESSED_DIR / "heading_chunks.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump([chunk.dict() for chunk in all_chunks], f, ensure_ascii=False, indent=2)
        
        log.info(f"Saved chunks to {output_file}")
        
        # Insert chunks into database
        chunk_ids = db_service.insert_chunks(all_chunks)
        
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
        
        log.info("PDF processing with heading-based chunking completed successfully")
        
    except Exception as e:
        log.error(f"Error processing PDFs: {e}")
        raise

if __name__ == "__main__":
    main()
