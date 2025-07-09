"""
Script to build embeddings and FAISS index from heading-based chunks
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.services.pdf_processor import PDFProcessor
from src.services.embedding_service import EmbeddingService
from src.services.database_service import DatabaseService
from src.services.faiss_service import FAISSService
from src.utils.logger import log


def main():
    """Main function to build embeddings and FAISS index from heading-based chunks"""
    log.info("Starting embedding and index building process for heading-based chunks...")
    
    try:
        # Initialize services
        pdf_processor = PDFProcessor()
        embedding_service = EmbeddingService()
        db_service = DatabaseService()
        faiss_service = FAISSService()
        
        # Load processed heading chunks
        log.info("Loading processed heading chunks...")
        chunks = pdf_processor.load_heading_chunks_from_file()
        
        if not chunks:
            log.error("No heading chunks found. Please run process_pdfs_with_headings.py first.")
            return
        
        log.info(f"Loaded {len(chunks)} heading-based chunks")
        
        # Clear existing data
        log.info("Clearing existing database data...")
        db_service.clear_all_data()
        
        # Insert chunks into database
        log.info("Inserting chunks into database...")
        chunk_ids = db_service.insert_chunks(chunks)
        
        # Create embeddings
        log.info("Creating embeddings...")
        texts = [chunk.content for chunk in chunks]
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
        
        # Print statistics
        db_stats = db_service.get_database_stats()
        faiss_stats = faiss_service.get_index_stats()
        
        log.info("=== Build Complete ===")
        log.info(f"Database stats: {db_stats}")
        log.info(f"FAISS stats: {faiss_stats}")
        log.info(f"Embedding dimension: {embedding_service.get_embedding_dimension()}")
        
        # Test search functionality
        log.info("Testing search functionality...")
        test_query = "thông tin tuyển sinh"
        query_embedding = embedding_service.create_embedding(test_query)
        
        search_results = faiss_service.search(query_embedding, top_k=3)
        log.info(f"Test search results for '{test_query}':")
        
        for i, (chunk_id, score) in enumerate(search_results, 1):
            chunk_data = db_service.get_chunk_by_id(chunk_id)
            if chunk_data:
                log.info(f"  {i}. Score: {score:.4f}")
                log.info(f"     Source: {chunk_data['source_file']}")
                log.info(f"     Content: {chunk_data['content'][:100]}...")
        
        log.info("Heading-based embedding and index building completed successfully!")
        
    except Exception as e:
        log.error(f"Error in heading-based embedding building process: {e}")
        raise


if __name__ == "__main__":
    main()