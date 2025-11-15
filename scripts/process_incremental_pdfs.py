"""
Script to incrementally process new PDFs from data/not_process folder
and add them to existing database without losing current data
"""

import json
import sys
import numpy as np
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.utils.logger import log
from src.services.pdf_processor import PDFProcessor
from src.services.embedding_service import EmbeddingService
from src.services.database_service import DatabaseService
from src.services.faiss_service import FAISSService
from config.settings import PROCESSED_DIR, EMBEDDING_MODEL, BM25_INDEX_PATH
import pickle
from rank_bm25 import BM25Okapi


def get_processed_files() -> set:
    """Get list of already processed files from database"""
    try:
        db_service = DatabaseService()
        processed_files = db_service.get_processed_files()
        log.info(f"Found {len(processed_files)} already processed files")
        return set(processed_files)
    except Exception as e:
        log.error(f"Error getting processed files: {e}")
        return set()


def get_new_pdf_files(not_process_dir: Path, processed_files: set) -> List[Path]:
    """Get list of new PDF files that haven't been processed yet"""
    pdf_files = list(not_process_dir.glob("*.pdf"))
    new_files = []

    for pdf_file in pdf_files:
        if pdf_file.name not in processed_files:
            new_files.append(pdf_file)
            log.info(f"New file found: {pdf_file.name}")
        else:
            log.info(f"File already processed: {pdf_file.name}")

    return new_files


def backup_current_data():
    """Create backup of current chunks file"""
    chunks_file = PROCESSED_DIR / "heading_chunks.json"
    if chunks_file.exists():
        import time

        backup_file = PROCESSED_DIR / f"heading_chunks_backup_{int(time.time())}.json"
        import shutil

        shutil.copy2(chunks_file, backup_file)
        log.info(f"Backup created: {backup_file}")
        return backup_file
    return None


def load_existing_chunks() -> List[Dict[Any, Any]]:
    """Load existing chunks from file"""
    chunks_file = PROCESSED_DIR / "heading_chunks.json"
    if chunks_file.exists():
        try:
            with open(chunks_file, "r", encoding="utf-8") as f:
                chunks = json.load(f)
            log.info(f"Loaded {len(chunks)} existing chunks")
            return chunks
        except Exception as e:
            log.error(f"Error loading existing chunks: {e}")
            return []
    else:
        log.warning("No existing chunks file found")
        return []


def save_updated_chunks(all_chunks: List[Dict[Any, Any]]):
    """Save updated chunks to file"""
    chunks_file = PROCESSED_DIR / "heading_chunks.json"
    try:
        with open(chunks_file, "w", encoding="utf-8") as f:
            json.dump(all_chunks, f, ensure_ascii=False, indent=4)
        log.info(f"Saved {len(all_chunks)} chunks to {chunks_file}")
    except Exception as e:
        log.error(f"Error saving chunks: {e}")
        raise


def rebuild_faiss_index(
    db_service: DatabaseService,
    embedding_service: EmbeddingService,
    faiss_service: FAISSService,
):
    """Rebuild FAISS index with all chunks including new ones"""
    log.info("Rebuilding FAISS index...")

    # Get all chunks from database
    all_chunks = db_service.get_all_chunks()
    if not all_chunks:
        log.error("No chunks found in database")
        return

    log.info(f"Processing {len(all_chunks)} chunks for FAISS index")

    # Create embeddings for all chunks
    chunk_texts = [chunk["content"] for chunk in all_chunks]
    chunk_ids = [chunk["id"] for chunk in all_chunks]

    # Generate embeddings in batches
    batch_size = 50
    all_embeddings = []

    for i in range(0, len(chunk_texts), batch_size):
        batch_texts = chunk_texts[i : i + batch_size]
        batch_embeddings = embedding_service.create_embeddings_batch(batch_texts)
        all_embeddings.extend(batch_embeddings)
        log.info(
            f"Generated embeddings for batch {i//batch_size + 1}/{(len(chunk_texts) + batch_size - 1)//batch_size}"
        )

    # Rebuild FAISS index with all embeddings
    all_embeddings_array = np.array(all_embeddings)
    faiss_service.rebuild_index(all_embeddings_array, chunk_ids)

    log.info("FAISS index rebuilt successfully")


def rebuild_bm25_index():
    """Rebuild BM25 index with all chunks"""
    log.info("Rebuilding BM25 index...")

    try:
        db_service = DatabaseService()
        all_chunks = db_service.get_all_chunks()

        if not all_chunks:
            log.error("No chunks found for BM25 index")
            return

        # Prepare texts for BM25
        chunk_texts = [chunk["content"] for chunk in all_chunks]
        tokenized_texts = [text.split() for text in chunk_texts]

        # Create BM25 index
        bm25 = BM25Okapi(tokenized_texts)

        # Save BM25 index
        with open(BM25_INDEX_PATH, "wb") as f:
            pickle.dump(bm25, f)

        log.info(f"BM25 index rebuilt with {len(chunk_texts)} chunks")

    except Exception as e:
        log.error(f"Error rebuilding BM25 index: {e}")


def main():
    """Main function to incrementally process new PDFs"""

    log.info("Starting incremental PDF processing...")

    try:
        # Define paths
        not_process_dir = Path("data/not_process_2")

        if not not_process_dir.exists():
            log.error(f"Directory {not_process_dir} does not exist")
            return

        # Initialize services
        pdf_processor = PDFProcessor()
        embedding_service = EmbeddingService(model_name=EMBEDDING_MODEL)
        db_service = DatabaseService()
        faiss_service = FAISSService()

        # Get already processed files
        processed_files = get_processed_files()

        # Get new PDF files to process
        new_pdf_files = get_new_pdf_files(not_process_dir, processed_files)

        if not new_pdf_files:
            log.info("No new PDF files to process")
            return

        log.info(f"Found {len(new_pdf_files)} new PDF files to process")

        # Create backup
        backup_file = backup_current_data()

        # Load existing chunks
        existing_chunks = load_existing_chunks()

        # Process new PDF files
        new_chunks = []  # Keep original DocumentChunk objects for database operations
        new_chunks_for_json = []  # Dictionaries for JSON serialization

        for pdf_file in new_pdf_files:
            log.info(f"Processing {pdf_file.name}...")

            try:
                # Process PDF with heading-based chunking
                chunks = pdf_processor.process_pdf_with_headings(pdf_file)

                if not chunks:
                    log.warning(f"No chunks created from {pdf_file.name}")
                    continue

                log.info(f"Created {len(chunks)} chunks from {pdf_file.name}")

                # Keep original objects for database operations
                new_chunks.extend(chunks)

                # Convert to dictionaries for JSON serialization
                chunk_dicts = [
                    chunk.model_dump() if hasattr(chunk, "model_dump") else chunk
                    for chunk in chunks
                ]
                new_chunks_for_json.extend(chunk_dicts)

            except Exception as e:
                log.error(f"Error processing {pdf_file.name}: {e}")
                continue

        if not new_chunks:
            log.warning("No new chunks were created")
            return

        log.info(f"Total new chunks created: {len(new_chunks)}")

        # Combine existing and new chunks for JSON file
        all_chunks_for_json = existing_chunks + new_chunks_for_json

        # Save updated chunks file (using dictionaries)
        save_updated_chunks(all_chunks_for_json)

        # Insert new chunks into database
        log.info("Inserting new chunks into database...")
        chunk_ids = db_service.insert_chunks(new_chunks)

        if not chunk_ids:
            log.error("Failed to insert chunks into database")
            return

        log.info(f"Inserted {len(chunk_ids)} new chunks into database")

        # Create embeddings for new chunks only
        log.info("Creating embeddings for new chunks...")
        new_chunk_texts = [chunk.content for chunk in new_chunks]
        new_embeddings = embedding_service.create_embeddings_batch(new_chunk_texts)

        if new_embeddings is None or len(new_embeddings) == 0:
            log.error("Failed to create embeddings")
            return

        # Insert new embeddings into database
        log.info("Inserting new embeddings into database...")
        db_service.insert_embeddings(chunk_ids, new_embeddings)

        # Rebuild FAISS index with all data
        rebuild_faiss_index(db_service, embedding_service, faiss_service)

        # Rebuild BM25 index
        rebuild_bm25_index()

        # Final statistics
        total_chunks = len(existing_chunks) + len(new_chunks_for_json)
        log.info("Incremental processing completed successfully!")
        log.info(f"Previous chunks: {len(existing_chunks)}")
        log.info(f"New chunks added: {len(new_chunks_for_json)}")
        log.info(f"Total chunks: {total_chunks}")

        # Verify database
        db_chunk_count = db_service.get_chunk_count()
        log.info(f"Database verification - Total chunks in DB: {db_chunk_count}")

        if backup_file:
            log.info(f"Backup file created at: {backup_file}")

    except Exception as e:
        log.error(f"Error in incremental processing: {e}")
        raise


if __name__ == "__main__":
    main()
