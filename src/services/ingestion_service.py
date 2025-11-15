"""
Ingestion Service for automatic PDF processing and indexing
Monitors PDF directory and processes new files automatically
"""

import asyncio
import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
from src.utils.logger import log
from config.settings import (
    PDF_WATCH_DIR,
    PROCESSED_PDF_DIR,
    INGESTION_CHECK_INTERVAL,
    AUTO_INGEST_ON_STARTUP,
)


class PDFFileHandler(FileSystemEventHandler):
    """Handler for PDF file system events"""

    def __init__(self, ingestion_service):
        """
        Initialize PDF file handler

        Args:
            ingestion_service: Reference to IngestionService
        """
        self.ingestion_service = ingestion_service

    def on_created(self, event):
        """Handle file creation event"""
        if event.is_directory:
            return

        if event.src_path.lower().endswith(".pdf"):
            log.info(f"📄 New PDF detected: {event.src_path}")
            # Schedule processing
            asyncio.create_task(self.ingestion_service.process_pdf(event.src_path))

    def on_modified(self, event):
        """Handle file modification event"""
        if event.is_directory:
            return

        if event.src_path.lower().endswith(".pdf"):
            log.info(f"📝 PDF modified: {event.src_path}")
            # Schedule reprocessing
            asyncio.create_task(self.ingestion_service.process_pdf(event.src_path))


class IngestionService:
    """Service for automatic PDF ingestion and processing"""

    def __init__(
        self,
        db_service,
        embedding_service,
        pdf_processor,
        hybrid_retrieval_service=None,
    ):
        """
        Initialize Ingestion Service

        Args:
            db_service: PostgreSQL database service
            embedding_service: Embedding service
            pdf_processor: PDF processor service
            hybrid_retrieval_service: Optional hybrid retrieval service for index updates
        """
        self.db_service = db_service
        self.embedding_service = embedding_service
        self.pdf_processor = pdf_processor
        self.hybrid_retrieval_service = hybrid_retrieval_service

        self.watch_dir = Path(PDF_WATCH_DIR)
        self.processed_dir = Path(PROCESSED_PDF_DIR)
        self.observer = None
        self.processed_files = set()

        # Create directories if they don't exist
        self.watch_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        log.info(f"📁 Watching directory: {self.watch_dir}")
        log.info(f"📁 Processed directory: {self.processed_dir}")

    async def process_pdf(self, pdf_path: str) -> bool:
        """
        Process a single PDF file

        Args:
            pdf_path: Path to PDF file

        Returns:
            True if processing was successful
        """
        try:
            pdf_path = Path(pdf_path)

            if not pdf_path.exists():
                log.warning(f"⚠️ PDF file not found: {pdf_path}")
                return False

            if pdf_path.suffix.lower() != ".pdf":
                log.warning(f"⚠️ File is not a PDF: {pdf_path}")
                return False

            log.info(f"🔄 Processing PDF: {pdf_path.name}")

            # Check if already processed
            if pdf_path.name in self.processed_files:
                log.info(f"⏭️ PDF already processed: {pdf_path.name}")
                return True

            # Extract text and create chunks
            log.info(f"📖 Extracting text from {pdf_path.name}...")
            chunks = await asyncio.to_thread(
                self.pdf_processor.process_pdf, str(pdf_path)
            )

            if not chunks:
                log.warning(f"⚠️ No chunks extracted from {pdf_path.name}")
                return False

            log.info(f"✂️ Created {len(chunks)} chunks from {pdf_path.name}")

            # Insert chunks into database
            log.info(f"💾 Inserting chunks into database...")
            chunk_ids = self.db_service.insert_chunks(chunks)

            # Generate embeddings
            log.info(f"🧠 Generating embeddings for {len(chunk_ids)} chunks...")
            embeddings = await asyncio.to_thread(
                self.embedding_service.generate_embeddings,
                [chunk.content for chunk in chunks],
            )

            # Insert embeddings
            log.info(f"💾 Inserting embeddings into database...")
            self.db_service.insert_embeddings(chunk_ids, embeddings)

            # Update BM25 index if available
            if self.hybrid_retrieval_service:
                log.info(f"🔨 Rebuilding BM25 index...")
                self.hybrid_retrieval_service.rebuild_bm25_index()

            # Move processed file
            processed_path = self.processed_dir / pdf_path.name
            pdf_path.rename(processed_path)
            self.processed_files.add(pdf_path.name)

            log.info(f"✅ Successfully processed {pdf_path.name}")
            log.info(
                f"   - Chunks: {len(chunks)}, Embeddings: {len(embeddings)}, "
                f"Moved to: {processed_path}"
            )

            return True

        except Exception as e:
            log.error(f"❌ Error processing PDF {pdf_path}: {e}")
            return False

    async def process_directory(self, directory: Optional[Path] = None) -> int:
        """
        Process all PDF files in a directory

        Args:
            directory: Directory to process (defaults to watch_dir)

        Returns:
            Number of successfully processed files
        """
        if directory is None:
            directory = self.watch_dir

        try:
            directory = Path(directory)
            pdf_files = list(directory.glob("*.pdf"))

            if not pdf_files:
                log.info(f"ℹ️ No PDF files found in {directory}")
                return 0

            log.info(f"📚 Found {len(pdf_files)} PDF files to process")

            processed_count = 0
            for pdf_file in pdf_files:
                success = await self.process_pdf(str(pdf_file))
                if success:
                    processed_count += 1

            log.info(f"✅ Processed {processed_count}/{len(pdf_files)} files")
            return processed_count

        except Exception as e:
            log.error(f"❌ Error processing directory {directory}: {e}")
            return 0

    def start_watching(self):
        """Start watching for new PDF files"""
        try:
            log.info("👀 Starting PDF file watcher...")

            # Create observer
            self.observer = Observer()

            # Create event handler
            event_handler = PDFFileHandler(self)

            # Schedule observer
            self.observer.schedule(event_handler, str(self.watch_dir), recursive=False)

            # Start observer
            self.observer.start()

            log.info("✅ PDF file watcher started")

        except Exception as e:
            log.error(f"❌ Error starting file watcher: {e}")
            raise

    def stop_watching(self):
        """Stop watching for new PDF files"""
        try:
            if self.observer:
                self.observer.stop()
                self.observer.join()
                log.info("✅ PDF file watcher stopped")
        except Exception as e:
            log.error(f"❌ Error stopping file watcher: {e}")

    async def run_periodic_check(self):
        """Run periodic check for new PDFs"""
        try:
            log.info(f"⏰ Starting periodic PDF check (interval: {INGESTION_CHECK_INTERVAL}s)")

            while True:
                await asyncio.sleep(INGESTION_CHECK_INTERVAL)
                log.info("🔍 Checking for new PDFs...")
                await self.process_directory()

        except asyncio.CancelledError:
            log.info("⏹️ Periodic check cancelled")
        except Exception as e:
            log.error(f"❌ Error in periodic check: {e}")

    def get_ingestion_stats(self) -> dict:
        """Get ingestion service statistics"""
        return {
            "watch_directory": str(self.watch_dir),
            "processed_directory": str(self.processed_dir),
            "processed_files_count": len(self.processed_files),
            "check_interval": INGESTION_CHECK_INTERVAL,
            "auto_ingest_on_startup": AUTO_INGEST_ON_STARTUP,
        }

