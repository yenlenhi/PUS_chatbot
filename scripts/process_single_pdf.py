"""
Script to process a single PDF file and add its chunks to the database
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.services.pdf_processor import PDFProcessor
from src.services.database_service import DatabaseService
from src.services.embedding_service import EmbeddingService
from src.services.faiss_service import FAISSService
from src.utils.logger import log


def main():
    """Process a single PDF file and add to database"""
    if len(sys.argv) < 2:
        print("Usage: python process_single_pdf.py <pdf_filename>")
        return
    
    pdf_filename = sys.argv[1]
    log.info(f"Processing single PDF: {pdf_filename}")
    
    # Initialize services
    pdf_processor = PDFProcessor()
    db_service = DatabaseService()
    embedding_service = EmbeddingService()
    faiss_service = FAISSService()
    
    # Process the PDF file
    pdf_path = pdf_processor.pdf_dir / pdf_filename
    if not pdf_path.exists():
        log.error(f"PDF file not found: {pdf_path}")
        return
    
    # Process PDF to chunks
    chunks = pdf_processor.process_pdf_to_chunks(pdf_path)
    
    if not chunks:
        log.warning(f"No chunks created from {pdf_filename}")
        return
    
    log.info(f"Created {len(chunks)} chunks from {pdf_filename}")
    
    # Insert chunks into database
    chunk_ids = db_service.insert_chunks(chunks)
    
    # Create embeddings
    texts = [chunk.content for chunk in chunks]
    embeddings = embedding_service.create_embeddings_batch(texts)
    
    # Insert embeddings into database
    db_service.insert_embeddings(chunk_ids, embeddings)
    
    # Load existing FAISS index
    faiss_service.load_index()
    
    # Add new embeddings to index
    faiss_service.add_to_index(embeddings, chunk_ids)
    
    # Save updated index
    faiss_service.save_index()
    
    log.info(f"Successfully processed {pdf_filename} and added {len(chunks)} chunks to the system")


if __name__ == "__main__":
    main()